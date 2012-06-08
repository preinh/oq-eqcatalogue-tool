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


from eqcatalogue import managers, selection
from eqcatalogue.serializers import mpl


class Homogeniser(object):

    def __init__(self, eventManager=None,
                 measureManager=None, grouper=None,
                 selector=None, serializer=None):

        self.eventManager = eventManager or managers.EventManager()
        self.measureManager = measureManager or managers.MeasureManager()
        self.grouper = grouper or selection.GroupMeasuresByEventSourceKey
        self.selector = selector or selection.RandomStrategy
        self.serializer = mpl or serializer
