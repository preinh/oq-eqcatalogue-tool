# Copyright (c) 2010-2012, GEM Foundation.
#
# eqcataloguetool is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EqCatalogueTool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with eqcataloguetool. If not, see <http://www.gnu.org/licenses/>.

"""
Module :mod:`eqcatalogue.selection` defines
:class:`MeasureManager`, :class:`MissingUncertaintyStrategy`,
:class:`MUSDiscard`, :class:`MUSSetEventMaximum`, :class:`MUSSetDefault`,
:class:`MeasureSelection`, :class:`Precise`, :class:`Random`,
:class:`AgencyRanking`.
"""

import abc
from random import choice
from math import sqrt, pow
from itertools import product
import re


class MeasureManager(object):

    def __init__(self, name):
        """
        Manage a list of quantitative measures

        :name: name of the magnitude scale
        """

        self.measures = []
        self.sigma = []
        self.name = name
        # holds a list of magnitude measure objects
        self.magnitude_measures = []

    def append(self, measure):
        """
        Add a measure to the list

        :measure: measure to add to the list
        """

        assert(measure and measure.value and measure.standard_error)
        self.magnitude_measures.append(measure)
        self.measures.append(measure.value)
        self.sigma.append(measure.standard_error)

    def __repr__(self):
        return self.name

    def __iter__(self):
        return self.measures.__iter__()

    def __len__(self):
        return len(self.measures)


class MissingUncertaintyStrategy(object):
    """
    Missing uncertainty strategy base class. Used to determine if a
    measure should be discarded or accepted when it does not have any
    uncertainty data associated, that is its standard error (sigma).
    When it is accepted it also provide a default value for its sigma.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def should_be_discarded(self, measure):
        pass

    def get_default(self, measure):
        pass


class MUSDiscard(MissingUncertaintyStrategy):
    """
    Missing uncertainty strategy class: discard measure if it has not a
    standard error.
    """

    def should_be_discarded(self, measure):
        ret = not measure.standard_error
        return ret

    def get_default(self, measure):
        return RuntimeError(
            "You can not get the default sigma for a discarded measure")


class MUSSetEventMaximum(MissingUncertaintyStrategy):
    """
    Missing uncertainty strategy class: discard measure if no measure of the
    same event has not a standard error, otherwise takes the maximum error
    (in the same event) as default.
    """

    def _get_event_errors(self, measure):
        errors = [m.standard_error for m in measure.event.measures
                  if m.standard_error]
        return errors

    def should_be_discarded(self, measure):
        errors = self._get_event_errors(measure)
        ret = not measure.standard_error and len(errors) == 0
        return ret

    def get_default(self, measure):
        errors = self._get_event_errors(measure)
        return max(errors)


class MUSSetDefault(MissingUncertaintyStrategy):
    """
    Missing uncertainty strategy class:

    Never discard the measure. Instead provide a default standard
    error if missing
    """

    def __init__(self, default):
        super(MUSSetDefault, self).__init__()
        self.default = default

    def get_default(self, _):
        return self.default

    def should_be_discarded(self, _):
        return False


class MeasureSelection(object):
    """
    Base class for all measure selection methods.

    A MeasureSelection defines a way to select a measure
    for an earthquake event. Subclasses of MeasureSelection
    must implement the select method.
    """

    def select(self, grouped_measures, native_scale, target_scale, mus):
        """
        Build a native_measure and a target_measure manager. Each
        manager is built by selecting a measure from a
        grouped_measures item. The selection is driven by the agency
        ranking.

        :grouped_measures: a dictionary where the keys identifies the events
            and the value are the list of measures associated with it.
        :native_scale: measure native scale.
        :target_scale: measure target scale.
        :mus: a missing uncertainty strategy object used to handle the case
            when no standard error of a measure is provided.
        """
        return self.__class__._select(grouped_measures, native_scale,
            target_scale, mus)


class Random(MeasureSelection):
    """
    Random apply the measure selection by
    choosing one random measure among the available ones.
    """

    @classmethod
    def _select(cls, grouped_measures, native_scale, target_scale, mus):
        native_measures = MeasureManager(native_scale)
        target_measures = MeasureManager(target_scale)

        for measures in grouped_measures.values():
            native_selection = []
            target_selection = []
            for measure in measures:
                if mus.should_be_discarded(measure):
                    continue
                if not measure.standard_error:
                    measure.standard_error = mus.get_default(measure)
                if measure.scale == native_scale:
                    native_selection.append(measure)
                if measure.scale == target_scale:
                    target_selection.append(measure)
            if native_selection and target_selection:
                native_measures.append(choice(native_selection))
                target_measures.append(choice(target_selection))

        return native_measures, target_measures


class Precise(MeasureSelection):
    """
    Precise apply the selection by
    choosing the best measure for precision
    among the available ones.
    """

    @classmethod
    def _precision_score(cls, native_measure, target_measure):
        """
        Calculate sigma value.
        :returns precision_score: measure score evaluation.
        """

        precision_score = sqrt(pow(native_measure, 2) + pow(target_measure, 2))
        return  precision_score

    @classmethod
    def _best_measures(cls, native_selection, target_selection):
        """
        Find the most precise measures by calculating
        the measures' precision score.
        """

        native_c_index = 0
        target_c_index = 1
        couples = list(product(native_selection, target_selection))
        sigma_couples = [Precise._precision_score(n.value, t.value)
                            for n, t in couples]
        min_val = min(sigma_couples)
        index_min_val = sigma_couples.index(min_val)
        return (couples[index_min_val][native_c_index],
               couples[index_min_val][target_c_index])

    @classmethod
    def _select(cls, grouped_measures, native_scale, target_scale, mus):
        native_measures = MeasureManager(native_scale)
        target_measures = MeasureManager(target_scale)

        for measures in grouped_measures.values():
            native_selection = []
            target_selection = []
            for measure in measures:
                if mus.should_be_discarded(measure):
                    continue
                if not measure.standard_error:
                    measure.standard_error = mus.get_default(measure)
                if measure.scale == native_scale:
                    native_selection.append(measure)
                if measure.scale == target_scale:
                    target_selection.append(measure)
            if native_selection and target_selection:
                couple = Precise._best_measures(
                    native_selection, target_selection)
                native_measures.append(couple[0])
                target_measures.append(couple[1])
        return native_measures, target_measures


class AgencyRanking(MeasureSelection):
    """
    Measure Selection based on AgencyRanking

    :param ranking:
        a dictionary where the keys are regexp that can match a
        magnitude scale and the value is a list of agency in the
        order of preference.
    """

    RANK_IF_NOT_FOUND = -1

    def __init__(self, ranking):

        super(AgencyRanking, self).__init__()
        self._ranking = ranking

    def calculate_rank(self, measure):
        """
        Calculate the rank of a measure.
        """
        for scale_pattern, agency_list_name in self._ranking.items():
            max_val = len(agency_list_name)
            scale_regexp = re.compile(scale_pattern)
            if scale_regexp.match(measure.scale):
                if measure.agency.source_key in agency_list_name:
                    return max_val - agency_list_name.index(
                        measure.agency.source_key)
        return self.__class__.RANK_IF_NOT_FOUND

    def select(self, grouped_measures,
               native_scale, target_scale,
               mus):
        """
        Build a native_measure and a target_measure manager. Each
        manager is built by selecting a measure from a
        grouped_measures item. The selection is driven by the agency
        ranking.

        :py:param:: grouped_measures
         A dictionary where the keys identifies the events and
        the value are the list of measures associated with it
        :py:param:: native_scale, target_scale
        The native and target scale used
        :py:param:: mus
        A missing uncertainty strategy object used to handle the case
        when no standard error of a measure is provided
        """
        native_measures = MeasureManager(native_scale)
        target_measures = MeasureManager(target_scale)

        for measures in grouped_measures.values():
            sorted_native_measures = []
            sorted_target_measures = []
            for measure in measures:
                if mus.should_be_discarded(measure):
                    continue
                if measure.scale == native_scale:
                    sorted_native_measures.append(
                        (self.calculate_rank(measure), measure))
                elif measure.scale == target_scale:
                    sorted_target_measures.append(
                        (self.calculate_rank(measure), measure))
                if not measure.standard_error:
                    measure.standard_error = mus.get_default(measure)
            sorted_native_measures.sort(reverse=True)
            sorted_target_measures.sort(reverse=True)

            if sorted_native_measures and sorted_target_measures:
                native_measures.append(sorted_native_measures[0][1])
                target_measures.append(sorted_target_measures[0][1])

        return native_measures, target_measures
