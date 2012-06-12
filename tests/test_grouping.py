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

import unittest

from eqcatalogue import models, filtering, grouping
from tests.test_filtering import load_fixtures


class AMeasureGrouperShould(unittest.TestCase):
    def setUp(self):
        self.cat_db = models.CatalogueDatabase(memory=True, drop=True)
        self.cat_db.recreate()
        self.measures = filtering.MeasureFilter()
        self.session = self.cat_db.session
        load_fixtures(self.session)

    def test_allows_grouping_of_measures(self):
        all_events = self.measures
        groups = all_events.group_measures()

        self.assertEqual(5, len(groups.keys()))
        self.assertEqual(['1008566', '1008567', '1008568',
                          '1008569', '1008570'], sorted(groups.keys()))

    def test_group_by_time_clustering(self):
        # Assess
        g1 = grouping.GroupMeasuresByHierarchicalClustering()
        g2 = grouping.GroupMeasuresByEventSourceKey()
        r2 = g2.group_measures(self.measures)

        # Act
        r1 = g1.group_measures(self.measures)

        # Assert
        self.assertEqual(len(r2.values()), len(r1.values()))
