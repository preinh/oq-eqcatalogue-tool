import unittest
import numpy as np
from tests.test_utils import in_data_dir

from matplotlib.testing.compare import compare_images

from eqcatalogue import regression, models
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

        native_values = np.random.uniform(3., 8.5, points)
        native_sigmas = np.random.uniform(0.02, 0.2, points)
        target_values = p2_0 + p2_1 * native_values +\
          p2_2 * (native_values ** 2.)
        target_values += np.random.normal(0., 1, points)
        target_sigmas = np.random.uniform(0.025, 0.2, points)
        native_measures = [models.MagnitudeMeasure(
            agency=None, event=None, origin=None,
            scale='Mtest', value=v[0], standard_error=v[1])
            for v in zip(native_values, native_sigmas)]
        target_measures = [models.MagnitudeMeasure(
            agency=None, event=None, origin=None,
            scale='Mtest', value=v[0], standard_error=v[1])
            for v in zip(target_values, target_sigmas)]

        emsr = regression.EmpiricalMagnitudeScalingRelationship(
            native_measures, target_measures)
        emsr.apply_regression_model(regression.LinearModel)
        emsr.apply_regression_model(regression.PolynomialModel,
                                    order=2)

        # Act
        plot(emsr, ACTUAL1)

        # Assert
        self.assertFalse(compare_images(EXPECTED1, ACTUAL1, tol=4))
