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
Implement Measure Selection Strategies
"""

import re

from eqcatalogue.managers import MeasureManager


class AgencyRanking(object):
    """
    Measure Selection based on AgencyRanking
    """
    def __init__(self, ranking):
        """
        Initialize an AgencyRanking object
        :py:param:: ranking
        a bdictionary where the keys are regexp that can match a
        magnitude scale and the value is a list of agency in the order
        of preference
        """
        self._ranking = ranking

    def calculate_rank(self, measure):
        for scale_pattern, agency_list_name in self._ranking.items():
            max_val = len(agency_list_name)
            scale_regexp = re.compile(scale_pattern)
            if scale_regexp.match(measure.scale):
                if measure.agency.source_key in agency_list_name:
                    return max_val - agency_list_name.index(
                        measure.agency.source_key)
        return -1

    def select(self, grouped_measures,
               native_scale, target_scale):
        """
        Build a native_measure and a target_measure manager. Each
        manager is built by selecting a measure from a
        grouped_measures item. The selection is driven by the agency
        ranking.

        :py:param:: grouped_measures
         A list of dictionary objects.
        Each dictionary at the key 'measures' has a list of measures
        as value
        :py:param:: native_scale, target_scale
        The native and target scale used
        """
        native_measures = MeasureManager(native_scale)
        target_measures = MeasureManager(target_scale)

        for m in grouped_measures:
            m['sorted_native_measures'] = []
            m['sorted_target_measures'] = []
            measures = m['measures']
            for measure in measures:
                if measure.scale == native_scale:
                    m['sorted_native_measures'].append(
                        (self.calculate_rank(measure), measure))
                elif measure.scale == target_scale:
                    m['sorted_target_measures'].append(
                        (self.calculate_rank(measure), measure))
            m['sorted_native_measures'].sort(reverse=True)
            m['sorted_target_measures'].sort(reverse=True)

            if m['sorted_native_measures'] and m['sorted_target_measures']:
                native_measures.append(m['sorted_native_measures'][0][1])
                target_measures.append(m['sorted_target_measures'][0][1])

        return native_measures, target_measures
