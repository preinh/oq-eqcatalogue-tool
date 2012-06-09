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
Simplified interface to catalogue tool homogeniser
"""


from eqcatalogue import selection, grouping, exceptions, models
from eqcatalogue.filtering import MeasureFilter
from eqcatalogue.regression import EmpiricalMagnitudeScalingRelationship
from eqcatalogue.serializers import mpl


class Homogeniser(object):
    """
    Earthquake Catalogue Homogeniser.

    Allow the homogenisation between different magnitude scales.

    This class allow to select a native and a target magnitude scale
    and plot different regression models against a set of values got
    from an event catalogue database.

    Each instance can
    1) apply filters to refine the considered set of events/measures
    2) use different measure clustering strategies
    3) use different measure selection strategies
    4) use different strategy to handle uncertainty
    """
    FILTERS_MAP = {
        'before': MeasureFilter.before,
        'after': MeasureFilter.after,
        'between': MeasureFilter.between,
        'agency__in': (lambda m, ags: m.with_agencies(*ags)),
        'scale__in': (lambda m, ss: m.with_magnitude_scales(*ss)),
        'within_polygon': MeasureFilter.within_polygon,
        'within_distance_from': MeasureFilter.within_distance_from_point,
        'magnitude__gt': lambda m, v: m.filter(
            models.MagnitudeMeasure.value > v)
    }

    def __init__(self,
                 native_scale=None, target_scale=None,
                 measure_filter=None,
                 grouper=None, selector=None,
                 missing_uncertainty_strategy=None,
                 serializer=None):

        self._measure_filter = measure_filter or MeasureFilter()
        self._grouper = grouper or grouping.GroupMeasuresByEventSourceKey()
        self._selector = selector or selection.RandomStrategy
        self._mu_strategy = (missing_uncertainty_strategy or
                             selection.MUSDiscard())
        self._serializer = mpl or serializer

        self._native_scale = native_scale
        self._target_scale = target_scale
        self._models = []

    def reset_filters(self):
        self._measure_filter = MeasureFilter()

    def reset_models(self):
        self._models = []

    def add_model(self, model_class, **model_kwargs):
        self._models.append((model_class, model_kwargs))

    def set_scales(self, native, target):
        """
        Set Native and Target Scale
        :param native
        The native magnitude scale (e.g. MW). Case Sensitive
        :param target
        The target magnitude scale (e.g. MW). Case Sensitive
        """
        self._native_scale = native
        self._target_scale = target

    def set_grouper(self, grouper_class, **grouper_args):
        self._grouper = grouper_class(**grouper_args)

    def set_selector(self, selector_class):
        self._selector = selector_class

    def set_missing_uncertainty_strategy(self, mu_strategy_class,
                                         **mu_strategy_args):
        self._mu_strategy = mu_strategy_class(**mu_strategy_args)

    def set_serializer(self, serializer):
        self._serializer = serializer

    def add_filter(self, **filter_kwargs):
        """
        Add a filter to the current measure filters
        See FILTERS_MAP for a list of the available filters
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
        Returns the current set of filtered events
        """
        return self._measure_filter.events()

    def measures(self):
        """
        Returns the current set of filtered measures
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
        Returns the current selected native measures to consider for
        regression
        """
        return self._selected_measures()[0]

    def selected_target_measures(self):
        """
        Returns the current selected native measures to consider for
        regression
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
        emsr = self._get_emsr()
        return self._serializer.plot(emsr,
                                     *serializer_args,
                                     **serializer_kwargs)
