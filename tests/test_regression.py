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
import numpy as np
from tests.test_utils import in_data_dir
from numpy.ma.testutils import assert_almost_equal

from eqcatalogue.regression import (EmpiricalMagnitudeScalingRelationship,
                                    LinearModel, PolynomialModel)
from eqcatalogue import managers
from eqcatalogue.importers import isf_bulletin
from eqcatalogue import models as catalogue
from eqcatalogue import selection


def _load_catalog():
    cat = catalogue.CatalogueDatabase(memory=True)
    cat.recreate()
    isf_bulletin.V1.import_events(
        file(in_data_dir('isc-query-small.html')),
        cat)
    return cat


class ShouldGroupMeasures(unittest.TestCase):
    def setUp(self):
        _load_catalog()
        self.event_manager = managers.EventManager()

    def test_group_by_time_clustering(self):
        # Assess
        g1 = managers.GroupMeasuresByHierarchicalClustering()
        g2 = managers.GroupMeasuresByEventSourceKey()
        r2 = g2.group_measures(self.event_manager)

        # Act
        r1 = g1.group_measures(self.event_manager)

        # Assert
        self.assertEqual(len(r2.values()), len(r1.values()))


class ShouldSelectMeasureByAgencyRanking(unittest.TestCase):

    def setUp(self):
        self.cat = _load_catalog()
        self.event_manager = managers.EventManager().with_agencies(
            'ISC', 'IDC', 'GCMT').with_magnitudes(
                'mb', 'MS', 'MW')
        self.events = self.event_manager.all()
        self.native_scale = 'mb'
        self.target_scale = 'MW'
        self.grouped_measures = {
            '1': self.events[0].measures,
            '2': self.events[1].measures,
            '3': self.events[2].measures}

    def test_simple_ranking(self):
        # Assess
        ranking = {'MW': ['GCMT', 'MOS', 'IDC'],
                   'mb': ['IDC', 'ISC']}

        # Act
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_measures(
            self.native_scale, self.target_scale,
            self.grouped_measures, selection.AgencyRanking(ranking),
            selection.MUSSetEventMaximum())

        # Assert
        self.assertEqual(len(emsr.native_measures), 3)
        self.assertEqual(len(emsr.target_measures), 3)
        for measure in emsr.native_measures.magnitude_measures:
            self.assertEqual(measure.scale, self.native_scale)
            self.assertEqual(measure.agency.source_key, 'IDC')
        for measure in emsr.target_measures.magnitude_measures:
            self.assertEqual(measure.scale, self.target_scale)
            self.assertEqual(measure.agency.source_key, 'GCMT',
                             "%s is not from GCMT" % measure)

    def test_pattern_ranking(self):
        # Assess
        ranking = {'mb': ['IDC'],
                   'M.': ['GCMT', 'ISC', 'ISCJB']}

        # Act
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events(
            self.native_scale, self.target_scale,
            self.event_manager, selection.AgencyRanking(ranking),
            selection.MUSSetEventMaximum())

        # Assert
        self.assertEqual(len(emsr.native_measures), 6)
        self.assertEqual(len(emsr.target_measures), 6)
        for measure in emsr.native_measures.magnitude_measures:
            self.assertEqual(measure.scale, self.native_scale)
            self.assertEqual(measure.agency.source_key, 'IDC')
        for measure in emsr.target_measures.magnitude_measures:
            self.assertEqual(measure.scale, self.target_scale)
            self.assertEqual(measure.agency.source_key, 'GCMT',
                             "%s is not from GCMT" % measure)

    def test_random_ranking(self):
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events(
            self.native_scale, self.target_scale,
            self.event_manager, selection.RandomSelection(),
            selection.MUSSetEventMaximum())

        self.assertEqual(len(emsr.native_measures), 6)
        self.assertEqual(len(emsr.target_measures), 6)

    def tearDown(self):
        self.cat.session.commit()


class ShouldPerformRegression(unittest.TestCase):

    def test_linear_regression(self):
        # Assess
        A = 0.85
        B = 1.03
        native_measures = managers.MeasureManager('mb')
        target_measures = managers.MeasureManager('Mw')
        native_measures.measures = np.random.uniform(3., 8.5, 1000)
        native_measures.sigma = np.random.uniform(0.02, 0.2, 1000)
        target_measures.measures = A + B * native_measures.measures
        target_measures.sigma = np.random.uniform(0.025, 0.2, 1000)
        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)

        # Act
        output = emsr.apply_regression_model(LinearModel)

        # Assert
        assert_almost_equal(np.array([A, B]), output.beta)
        self.assertTrue(output.res_var < 1e-20)

    def test_polynomial_regression(self):
        # Assess
        A = 0.046
        B = 0.556
        C = 0.673
        native_measures = managers.MeasureManager('mb')
        target_measures = managers.MeasureManager('Mw')
        native_measures.measures = np.random.uniform(3., 8.5, 1000)
        native_measures.sigma = np.random.uniform(0.02, 0.2, 1000)
        target_measures.measures = C + B * native_measures.measures +\
          A * (native_measures.measures ** 2.)
        target_measures.sigma = np.random.uniform(0.025, 0.2, 1000)
        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)

        # Act
        output = emsr.apply_regression_model(PolynomialModel,
                                             order=2)

        # Assert
        assert_almost_equal(np.array([C, B, A]), output.beta)
        self.assertTrue(output.res_var < 1e-20)
