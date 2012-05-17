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

from eqcatalogue.managers import MeasureManager


class AgencyRanking(object):
    """
    Measure Selection based on AgencyRanking
    """
    def __init__(self, ranking):
        """
        Initialize an AgencyRanking object
        :py:param:: ranking
        a dictionary where the keys are regexp that can match a
        magnitude scale and the value is a list of agency in the order
        of preference
        """
        self._ranking = ranking

    def select(self, grouped_measures,
               native_scale, target_scale):
        native_measures = MeasureManager(native_scale)
        target_measures = MeasureManager(target_scale)

        return native_measures, target_measures
