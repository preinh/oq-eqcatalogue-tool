import unittest
import numpy as np
from matplotlib.testing.compare import compare_images
from tests.test_importers import in_data_dir

from eqcatalogue import regression
from eqcatalogue import managers
from eqcatalogue.serializers.mpl import Plot


ACTUAL1 = in_data_dir('actual1.png')
EXPECTED1 = in_data_dir('expected1.png')


class ShoudPlotEMSR(unittest.TestCase):
    def test_plot_emsr(self):
        # Assess
        p2_0 = 0.046
        p2_1 = 0.556
        p2_2 = 0.673

        native_measures = managers.MeasureManager()
        target_measures = managers.MeasureManager()
        native_measures.measures = np.random.uniform(3., 8.5, 1000)
        native_measures.sigma = np.random.uniform(0.02, 0.2, 1000)
        target_measures.measures = p2_0 + p2_1 * native_measures.measures +\
          p2_2 * (native_measures.measures ** 2.)
        target_measures.sigma = np.random.uniform(0.025, 0.2, 1000)
        emsr = regression.EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)

        # Act
        emsr.apply_regression_model(regression.LinearModel)
        emsr.apply_regression_model(regression.PolynomialModel,
                                    order=2)
        emsr.apply_regression_model(regression.PolynomialModel,
                                    order=5)

        # Act
        Plot(emsr, ACTUAL1).save()

        # Assert
        self.assertTrue(compare_images(EXPECTED1, ACTUAL1, tol=0.001))
