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
Implement Measure Selection Strategies and Missing Uncertainty Handling
"""

import abc
from random import choice
from math import sqrt, pow
from itertools import product
import re

from eqcatalogue.managers import MeasureManager


class MUSDiscard(object):
    """
    Missing uncertainty strategy class:
    Discard Measure if it has not a standard error
    """
    def should_be_discarded(self, measure):
        ret = not measure.standard_error
        return ret


class MUSSetEventMaximum(MUSDiscard):
    """
    Missing uncertainty strategy class:

    Discard Measure if no measure of the same event has not a standard
    error, otherwise takes the maximum error (in the same event) as
    default
    """
    def _get_event_errors(self, measure):
        errors = [m.standard_error for m in measure.event.measures
                  if m.standard_error]
        return errors

    def should_be_discarded(self, measure):
        errors = self._get_event_errors(measure)
        ret = super(MUSSetEventMaximum, self).should_be_discarded(
           measure) and len(errors) == 0
        return ret

    def get_default(self, measure):
        errors = self._get_event_errors(measure)
        return max(errors)


class MUSSetDefault(object):
    """
    Missing uncertainty strategy class:

    Never discard the measure. Instead provide a default standard
    error if missing
    """

    def __init__(self, default):
        self.default = default

    def get_default(self, _):
        return self.default

    def should_be_discarded(self):
        return False


class MeasureSelection(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def select(self, grouped_measures, native_scale, target_scale, mus):
        return


class RandomStrategy(MeasureSelection):

    @classmethod
    def select(cls, grouped_measures, native_scale, target_scale, mus):
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


class PrecisionStrategy(MeasureSelection):

    @classmethod
    def _compute_sigma(cls, native_measure, target_measure):
        return sqrt(pow(native_measure, 2) + pow(target_measure, 2))

    @classmethod
    def _find_minimum_sigma(cls, native_selection, target_selection):
        native_c_index = 0
        target_c_index = 1
        couples = list(product(native_selection, target_selection))
        sigma_couples = [PrecisionStrategy._compute_sigma(n.value, t.value)
                            for n, t in couples]
        min_val = min(sigma_couples)
        index_min_val = sigma_couples.index(min_val)
        return (couples[index_min_val][native_c_index],
               couples[index_min_val][target_c_index])

    @classmethod
    def select(cls, grouped_measures, native_scale, target_scale, mus):
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
                couple = PrecisionStrategy._find_minimum_sigma(
                    native_selection, target_selection)
                native_measures.append(couple[0])
                target_measures.append(couple[1])
        return native_measures, target_measures


class AgencyRankingStrategy(MeasureSelection):
    """
    Measure Selection based on AgencyRanking
    """

    RANK_IF_NOT_FOUND = -1

    def __init__(self, ranking):
        """
        Initialize an AgencyRanking object
        :py:param:: ranking
        a dictionary where the keys are regexp that can match a
        magnitude scale and the value is a list of agency in the order
        of preference
        """
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
