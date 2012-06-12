# Copyright (c) 2010-2012, GEM Foundation.
#
# eqcatalogueTool is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# eqcatalogueTool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with eqcatalogueTool. If not, see <http://www.gnu.org/licenses/>.

"""
This module provides the main class that handles the homogenisation
between different magnitude scales value.
"""


from eqcatalogue import selection, grouping, exceptions, models
from eqcatalogue.filtering import MeasureFilter
from eqcatalogue.regression import EmpiricalMagnitudeScalingRelationship
from eqcatalogue.serializers import mpl


class Homogeniser(object):
    """
    This class allow to select a native and a target magnitude scale
    and plot different regression models against a set of values got
    from an Event Catalogue database.

    Each instance of this class can:

    1. apply filters to refine the considered set of events/measures;
    2. use different measure clustering grouping algorithm;
    3. use different measure selection algorithm;
    4. use different strategy to handle uncertainty.
    5. serialize or plot the results
    """
    FILTERS_MAP = {
        'before': MeasureFilter.before,
        'after': MeasureFilter.after,
        'between': (lambda m, timestamps: m.between(*timestamps)),
        'agency__in': (lambda m, ags: m.with_agencies(*ags)),
        'scale__in': (lambda m, ss: m.with_magnitude_scales(*ss)),
        'within_polygon': MeasureFilter.within_polygon,
        'within_distance_from_point': (
            lambda m, dp: m.within_distance_from_point(*dp)),
        'magnitude__gt': lambda m, v: m.filter(
            models.MagnitudeMeasure.value > v)
    }

    #: Filter arguments that can be used in the add_filter method
    AVAILABLE_FILTERS = FILTERS_MAP.keys()

    def __init__(self,
                 native_scale=None, target_scale=None,
                 measure_filter=None,
                 grouper=None, selector=None,
                 missing_uncertainty_strategy=None,
                 serializer=None):
        """
        Initialise a class instance given as input the native and the
        target magnitude scale.
        Moreover, it allows to setup an instance with low-level
        instance objects.

        :param native_scale: The native magnitude scale (case sensitive)
        :type native_scale: string

        :param target_cale: The target magnitude scale (case sensitive)
        :type target_scale: string

        :param measure_filter:
          A MeasureFilter instance object used to filter measures. If
          not given, a filter that selects all the measures is used as
          default.
        :type measure_filter: MeasureFilter

        :param grouper:
          A MeasureGrouper instance object used to group
          measures by seismic event. If not given, the grouping strategy
          based on the imported catalogue key is used.
        :type grouper: MeasureGrouper

        :param selector:
          A MeasureSelection instance object used to
          select a measure among a group of measures related to the same
          event. If not given, measure are selected randomly.
        :type selector: MeasureSelection

        :param missing_uncertainty_strategy:
          A MissingUncertaintyStrategy instance object used to handle
          incomplete knowledge of a measure error. If not given, a
          strategy that discards the magnitude values without a standard
          error is used.
        :type missing_uncertainty_strategy: MissingUncertaintyStrategy
        """
        self._measure_filter = measure_filter or MeasureFilter()
        self._grouper = grouper or grouping.GroupMeasuresByEventSourceKey()
        self._selector = selector or selection.Random()
        self._mu_strategy = (missing_uncertainty_strategy or
                             selection.MUSDiscard())
        self._serializer = mpl or serializer

        self._native_scale = native_scale
        self._target_scale = target_scale
        self._models = []

    def reset_filters(self):
        """
        Reset the filters back to the catch-all measure filter.
        """
        self._measure_filter = MeasureFilter()

    def reset_models(self):
        """
        Reset the regression models used for homogenisation
        """
        self._models = []

    def add_model(self, model_class, **model_kwargs):
        """
        Add a regression model to be calculated to homogenise
        magnitude values

        :param model_class:
          A class that implements the RegressionModel protocol.
          See :py:class:`eqcatalogue.regression` for the current
          admitted values

        Any other parameter is given as input to the constructor of
        `model_class`. E.g.::

          from eqcatalogue.regression import PolynomialModel
          an_homogeniser.add_model(PolynomialModel, order=3)

        """
        self._models.append((model_class, model_kwargs))

    def set_scales(self, native, target):
        """
        Set Native and Target Scale

        :param native:
         The native magnitude scale (e.g. ML). Case Sensitive
        :param target:
         The target magnitude scale (e.g. MW). Case Sensitive
        """
        self._native_scale = native
        self._target_scale = target

    def set_grouper(self, grouper_class, **grouper_args):
        """
        Set the algorithm used to group measures by event.

        :param grouper_class:
          A class that implements the MeasureGrouper protocol.
          See :py:class:`eqcatalogue.grouping` for the current
          admitted values

        Any other parameter is given as input to the constructor of
        `grouper_class`. E.g.::

         from eqcatalogue.grouping import GroupMeasuresByHierarchicalClustering
         an_homogeniser.set_grouper(GroupMeasuresByHierarchicalClustering)
        """
        self._grouper = grouper_class(**grouper_args)

    def set_selector(self, selector_class, **selector_args):
        """
        Set the algorithm used to select a measure among grouped
        measures.

        :param selector_class:
          A class that implements the MeasureSelection protocol.
          See :py:class:`eqcatalogue.selection` for the current
          admitted values

        Any other parameter is given as input to the constructor of
        `selector_class`. E.g.::

          from eqcatalogue.selection import Precise
          an_homogeniser.set_selector(Precise)
        """
        self._selector = selector_class(**selector_args)

    def set_missing_uncertainty_strategy(self, mu_strategy_class,
                                         **mu_strategy_args):
        """
        Set the algorithm used to handle situations where uncertainty
        data are missing in a measure.

        :param mu_strategy_class:
          A class that implements the MissingUncertaintyStrategy protocol.
          See :py:class:`eqcatalogue.selection` for the current
          admitted values

        Any other parameter is given as input to the constructor of
        `mu_strategy_class`. E.g.::

          from eqcatalogue.selection import MUSSetDefault
          an_homogeniser.set_missing_uncertainty_strategy(
            MUSSetDefault, default=3)
        """
        self._mu_strategy = mu_strategy_class(**mu_strategy_args)

    def set_serializer(self, serializer):
        self._serializer = serializer

    def add_filter(self, **filter_kwargs):
        """
        Add a filter to the current measure filter query.

        E.g.
        homo = Homogeniser()
        homo.add_filter(agency__in=a_list_agency)
        homo.add_filter(magnitude__gt=4, within_polygon=a_polygon)

        See FILTERS_MAP for a list of the available filter keyword argument
        """
        measure_filter = MeasureFilter()
        for filter_desc, value in filter_kwargs.items():
            filter_fn = self._get_filter_fn(filter_desc)
            new_filter = filter_fn(MeasureFilter(), value)
            measure_filter = measure_filter.combine(new_filter)
        self._measure_filter = self._measure_filter.combine(measure_filter)

    def _get_filter_fn(self, filter_desc):
        if not filter_desc in self.__class__.FILTERS_MAP:
            raise exceptions.InvalidFilter(
                """%s does not indicate any known filter.
        Valid filter keywords includes: %s""" % (
            filter_desc, "\n".join(self.__class__.FILTERS_MAP.keys())))
        return self.__class__.FILTERS_MAP[filter_desc]

    def events(self):
        """
        :return: the current set of filtered events.
        :rtype: a list of :py:class:`~eqcatalogue.models.Event` instances
        """
        return self._measure_filter.events()

    def measures(self):
        """
        :return: the current set of filtered measures.
        :rtype:
          a list of :py:class:`~eqcatalogue.models.MagnitudeMeasure` instances
        """
        return self._measure_filter.all()

    def grouped_measures(self):
        """
        Returns the measures grouped by event according with the
        current grouping strategy
        """
        return self._measure_filter.group_measures(self._grouper)

    def _selected_measures(self):
        return self._selector.select(self.grouped_measures(),
                                     self._native_scale,
                                     self._target_scale,
                                     self._mu_strategy)

    def selected_native_measures(self):
        """
        :return:
          the current selected native measures to consider for
          regression.
        :rtype:
          a :py:class:`~eqcatalogue.selection.MeasureManager`
          instance
        """
        return self._selected_measures()[0]

    def selected_target_measures(self):
        """
        :return:
          the current selected native measures to consider for
          regression
        :rtype:
          a :py:class:`~eqcatalogue.selection.MeasureManager`
          instance
        """
        return self._selected_measures()[1]

    def _get_emsr(self):
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_measures(
            self._native_scale, self._target_scale,
            self.grouped_measures(), self._selector,
            self._mu_strategy)
        for model_class, model_kwargs in self._models:
            emsr.apply_regression_model(model_class,
                                        **model_kwargs)
        return emsr

    def serialize(self, *serializer_args, **serializer_kwargs):
        """
        Plot the selected native magnitude values against the target
        ones and the considered regression models to `filename`
        """
        emsr = self._get_emsr()
        return self._serializer.plot(emsr,
                                     *serializer_args,
                                     **serializer_kwargs)

    def plot(self, *args, **kwargs):
        """
        An alias for serialize
        """
        self.serialize(*args, **kwargs)
