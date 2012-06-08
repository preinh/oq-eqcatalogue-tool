import unittest
import numpy as np
from tests.test_utils import in_data_dir

from matplotlib.testing.compare import compare_images

from eqcatalogue import regression
from eqcatalogue import selection
from eqcatalogue.serializers.mpl import plot

ACTUAL1 = in_data_dir('actual1.png')
EXPECTED1 = in_data_dir('expected1.png')


class ShoudPlotEMSR(unittest.TestCase):
    def test_plot_emsr(self):
        # Assess
        p2_0 = 0.046
        p2_1 = 0.556
        p2_2 = 0.673
        points = 40

        native_measures = selection.MeasureManager('Mtest')
        target_measures = selection.MeasureManager('Mtest2')
        native_measures.measures = np.random.uniform(3., 8.5, points)
        native_measures.sigma = np.random.uniform(0.02, 0.2, points)
        target_measures.measures = p2_0 + p2_1 * native_measures.measures +\
          p2_2 * (native_measures.measures ** 2.)
        target_measures.measures += np.random.normal(0., 1, points)
        target_measures.sigma = np.random.uniform(0.025, 0.2, points)
        emsr = regression.EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)
        emsr.apply_regression_model(regression.LinearModel)
        emsr.apply_regression_model(regression.PolynomialModel,
                                    order=2)

        # Act
        plot(emsr, ACTUAL1)

        # Assert
        self.assertFalse(compare_images(EXPECTED1, ACTUAL1, tol=4))
