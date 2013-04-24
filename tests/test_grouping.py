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
import random
from datetime import datetime

from eqcatalogue import models, filtering, grouping
from tests.test_filtering import load_fixtures


class AMeasureGrouperShould(unittest.TestCase):
    def setUp(self):
        self.cat_db = models.CatalogueDatabase(memory=True, drop=True)
        self.measures = filtering.Criteria()
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
        for group in r2.values():
            # groups should be set-equal
            group = set(group)
            self.assertTrue(group in [set(g) for g in r1.values()])
        self.assertEqual(len(r1.values()), len(r2.values()))

    def test_group_by_sequential_clustering(self):
        # Assess
        g1 = grouping.GroupMeasuresBySequentialClustering(
            time_window=10, space_window=200)
        g2 = grouping.GroupMeasuresByEventSourceKey()
        r2 = g2.group_measures(self.measures)

        # Act
        r1 = g1.group_measures(self.measures)

        # Assert
        for group in r2.values():
            # groups should be set-equal
            group = set(group)
            self.assertTrue(group in [set(g) for g in r1.values()])
        self.assertEqual(len(r1.values()), len(r2.values()))


class ASequentialMeasureGrouperShould(unittest.TestCase):
    def setUp(self):
        """
        We create three events, i.e. group of measures.

        To challenge the grouper, the first event is near the second
        one in time but not in space. Moreover, the third event is
        near the second one in space but not in time.
        """
        catalogue = models.CatalogueDatabase()

        # create 3 events. Event1 is near Event2 in time but not in
        # space, Event2 is near Event3 in space but not in time
        self.n = 3
        events = [("event key %d" % i, "test event %d")
                  for i in range(0, self.n)]

        # create m positions for the first two events
        self.m = 10
        positions = [[catalogue.position_from_latlng(i * 10. + random.random(),
                                                     i * 10. + random.random())
                     for _ in range(0, self.m)]
                     for i in range(0, self.n - 1)]
        # add m positions for the third event with a distance < 1 from
        # the positions associated with the second event
        self.space_window = 500
        positions.append([catalogue.position_from_latlng(
            10. + random.random(),
            10. + random.random()) for j in range(0, self.m)])

        # similary for times
        times = [[datetime.fromtimestamp(i * 10. + random.random())
                  for _ in range(0, self.m)]
                 for i in range(0, self.n - 1)]
        self.time_window = 1
        times.insert(1, [datetime.fromtimestamp(random.random())
                         for j in range(0, self.m)])

        # create m origins for each event
        origins = [[dict(position=positions[i][j],
                         time=times[i][j],
                         origin_key=(i, j))
                   for j in range(0, self.m)]
                   for i in range(0, self.n)]

        an_agency = "test agency"
        # create corresponding measures
        self.measures = [models.MagnitudeMeasure(
            event_source=None,
            agency=an_agency,
            event_key=events[i][0],
            event_name=events[i][0],
            scale="Mw",
            value=i + j,
            **origins[i][j])
            for i in range(0, self.n)
            for j in range(0, self.m)]
        self.grouper = grouping.GroupMeasuresBySequentialClustering(
            time_window=self.time_window, space_window=self.space_window)

    def test_build_graph(self):
        graph = grouping.GroupMeasuresBySequentialClustering.build_graph(
            self.measures,
            models.MagnitudeMeasure.time_distance,
            0.5)

        for m1, related in graph.items():
            for m2 in related:
                self.assertTrue(abs(m1.time - m2.time).total_seconds() < 0.5)
                self.assertTrue(m1 != m2)

    def test_find_connected_components(self):
        cls = grouping.GroupMeasuresBySequentialClustering
        graph = cls.build_graph(
            [1, 2, 3, 9, 10, 11],
            lambda x, y: abs(x - y), 2)

        comps = cls.find_connected_components(graph)

        # check that components are disjoint
        for comp1 in comps:
            for comp2 in comps:
                if comp1 == comp2:
                    continue
                self.assertTrue(not set(comp1).intersection(set(comp2)))

    def test_group_measures_by_time(self):
        groups = self.grouper.group_measures_by_time(self.measures)

        self.assertEqual(2, len(groups))

        for measures in groups:
            self.assertTrue(self.m == len(measures) or
                            2 * self.m == len(measures))

    def test_group_measures_by_space(self):
        groups = self.grouper.group_measures_by_space(self.measures)

        self.assertEqual(2, len(groups))

        for measures in groups:
            self.assertTrue(self.m == len(measures) or
                            2 * self.m == len(measures))

    def test_group_sequentially(self):
        groups = self.grouper.group_measures(self.measures)

        self.assertEqual(3, len(groups))

        for measures in groups.values():
            self.assertEqual(self.m, len(measures))
            expected_group = measures[0].origin_key[0]

            for measure in measures:
                self.assertEqual(expected_group, measure.origin_key[0])

    def test_group_sequentially_with_magnitude(self):
        self.grouper = grouping.GroupMeasuresBySequentialClustering(
            time_window=self.time_window,
            space_window=self.space_window,
            magnitude_window=0.5)

        groups = self.grouper.group_measures(self.measures)

        self.assertEqual(self.m * self.n, len(groups))

        for measures in groups.values():
            self.assertEqual(1, len(measures))
