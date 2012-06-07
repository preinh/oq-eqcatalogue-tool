import unittest
import numpy as np
import os
from datetime import datetime
from numpy.ma.testutils import assert_almost_equal

from tests.test_utils import in_data_dir

from eqcatalogue import models, selection
from eqcatalogue.managers import EventManager
from eqcatalogue.regression import (EmpiricalMagnitudeScalingRelationship,
                                    LinearModel, PolynomialModel)
from eqcatalogue.serializers import mpl


DB = models.CatalogueDatabase(filename=in_data_dir('pluto.db'))

class CatalogueTool(unittest.TestCase):

    def test_first_config(self):
        events = EventManager().with_agencies("ISC", "BJI")
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events(
            "mb", "MS", events, selection.PrecisionStrategy)
        output = emsr.apply_regression_model(LinearModel)
        graph_filename = 'first_config.png'
        mpl.plot(emsr, in_data_dir(graph_filename))
        expected_beta = np.array([-2.36836, 1.49706])
        expected_res_var = 4.84118

        np.allclose(expected_beta, output.beta)
        self.assertAlmostEqual(expected_res_var, output.res_var, places=5)
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))

    def test_second_config(self):
        events = EventManager().with_agency("ISC").before(datetime.now())
        ranking = {"ML": ["ISC", "IDC"], "mb": ["ISC", "FUNV"]}
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events(
            "ML", "mb", events, selection.AgencyRankingStrategy(ranking))
        emsr.apply_regression_model(LinearModel)
        output = emsr.apply_regression_model(PolynomialModel, order=2)
        graph_filename = 'second_config.png'
        mpl.plot(emsr, in_data_dir(graph_filename))
        expected_beta = np.array([-2.36836, 1.49706])
        expected_res_var = 1.68513

        np.allclose(expected_beta, output.beta)
        self.assertAlmostEqual(expected_res_var, output.res_var, places=5)
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))

    def test_third_config(self):
        pass

    def test_fourth_config(self):
        pass

    def test_fifth_config(self):
        pass

    def test_sixth_config(self):
        pass

    def test_seventh_config(self):
        pass

    def test_eighth_config(self):
        pass
