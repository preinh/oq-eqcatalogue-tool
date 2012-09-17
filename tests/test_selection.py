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
from eqcatalogue import filtering, grouping
from eqcatalogue import selection, models
from tests.test_utils import _load_catalog


class ShouldSelectMeasureByAgencyRanking(unittest.TestCase):

    def setUp(self):
        _load_catalog()
        measures = filtering.C(agency__in=['ISC', 'IDC', 'GCMT'],
                               scale__in=['mb', 'MS', 'MW'])
        self.native_scale = 'mb'
        self.target_scale = 'MW'
        grouper = grouping.GroupMeasuresByEventSourceKey()
        self.grouped_measures = grouper.group_measures(measures)
        self.mus = selection.MUSSetDefault(1)

    def test_simple_ranking(self):
        # Assess
        ranking = {'MW': ['GCMT', 'MOS', 'IDC'],
                   'mb': ['IDC', 'ISC']}

        # Act
        n, t = selection.AgencyRanking(ranking).select(
            self.grouped_measures,
            self.native_scale, self.target_scale, self.mus)

        # Assert
        self.assertEqual(len(n), 6)
        self.assertEqual(len(t), 6)
        for measure in n:
            self.assertEqual(measure.scale, self.native_scale)
            self.assertEqual(measure.agency.source_key, 'IDC')
        for measure in t:
            self.assertEqual(measure.scale, self.target_scale)
            self.assertEqual(measure.agency.source_key, 'GCMT',
                             "%s is not from GCMT" % measure)

    def test_pattern_ranking(self):
        # Assess
        ranking = {'mb': ['IDC'],
                   'M.': ['GCMT', 'ISC', 'ISCJB']}

        # Act
        n, t = selection.AgencyRanking(ranking).select(
            self.grouped_measures,
            self.native_scale, self.target_scale, self.mus)

        # Assert
        self.assertEqual(len(n), 6)
        self.assertEqual(len(t), 6)
        for measure in n:
            self.assertEqual(measure.scale, self.native_scale)
            self.assertEqual(measure.agency.source_key, 'IDC')
        for measure in t:
            self.assertEqual(measure.scale, self.target_scale)
            self.assertEqual(measure.agency.source_key, 'GCMT',
                             "%s is not from GCMT" % measure)

    def test_random_ranking(self):
        n, t = selection.Random().select(
            self.grouped_measures,
            self.native_scale, self.target_scale, self.mus)

        self.assertEqual(len(n), 6)
        self.assertEqual(len(t), 6)

    def test_minimum_sigma_selection(self):
        print self.grouped_measures
        n, t = selection.Precise().select(
            self.grouped_measures,
            self.native_scale, self.target_scale, self.mus)

        self.assertEqual(len(n), 6)
        self.assertEqual(len(t), 6)

    def tearDown(self):
        models.CatalogueDatabase().session.commit()
