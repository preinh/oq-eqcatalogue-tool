import unittest
import numpy as np
from matplotlib.testing.compare import compare_images
from tests.test_importers import in_data_dir

from eqcatalogue import regression
from eqcatalogue import managers
from eqcatalogue.serializers.mpl import plot


ACTUAL1 = in_data_dir('actual1.png')
EXPECTED1 = in_data_dir('expected1.png')


class ShoudPlotEMSR(unittest.TestCase):
    def test_plot_emsr(self):
        # Assess
        p2_0 = 0.046
        p2_1 = 0.556
        p2_2 = 0.673

        native_measures = managers.MeasureManager('Mtest')
        target_measures = managers.MeasureManager('Mtest2')
        native_measures.measures = np.random.uniform(3., 8.5, 100)
        native_measures.sigma = np.random.uniform(0.02, 0.2, 100)
        target_measures.measures = p2_0 + p2_1 * native_measures.measures +\
          p2_2 * (native_measures.measures ** 2.)
        target_measures.sigma = np.random.uniform(0.025, 0.2, 100)
        emsr = regression.EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)
        emsr.apply_regression_model(regression.LinearModel)
        emsr.apply_regression_model(regression.PolynomialModel,
                                    order=2)
        emsr.apply_regression_model(regression.PolynomialModel,
                                    order=5)

        # Act
        plot(emsr, ACTUAL1)

        # Assert
        self.assertTrue(compare_images(EXPECTED1, ACTUAL1, tol=0.001))
