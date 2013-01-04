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
from numpy import allclose

from eqcatalogue.regression import (EmpiricalMagnitudeScalingRelationship,
                                    LinearModel, PolynomialModel)
from eqcatalogue import exceptions
from eqcatalogue import models as catalogue


class ShouldPerformRegression(unittest.TestCase):

    def test_linear_regression(self):
        # Assess
        A = 0.85
        B = 1.03
        native_measures = catalogue.MagnitudeMeasure.make_from_lists(
            'mb',
            np.random.uniform(3., 8.5, 1000),
            np.random.uniform(0.02, 0.2, 1000))
        target_measures = catalogue.MagnitudeMeasure.make_from_lists(
            "Mw",
            A + B * np.array([m.value for m in native_measures]),
            np.random.uniform(0.025, 0.2, 1000))
        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)

        # Act
        _, output = emsr.apply_regression_model(LinearModel)

        # Assert
        self.assertTrue(allclose(np.array([A, B]), output.beta))
        self.assertTrue(output.res_var < 1e-20)

    def test_polynomial_regression(self):
        # Assess
        A = 0.046
        B = 0.556
        C = 0.673
        native_measures = catalogue.MagnitudeMeasure.make_from_lists(
            'mb', np.random.uniform(3., 8.5, 1000),
            np.random.uniform(0.02, 0.2, 1000))
        target_measures = catalogue.MagnitudeMeasure.make_from_lists(
            'Mw',
            (C + B * np.array([m.value for m in native_measures]) +
             A * (np.array([m.value for m in native_measures]) ** 2.)),
             np.random.uniform(0.025, 0.2, 1000))
        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)

        # Act
        _, output = emsr.apply_regression_model(PolynomialModel,
                                             order=2)

        # Assert
        self.assertTrue(allclose(np.array([C, B, A]), output.beta))
        self.assertTrue(output.res_var < 1e-20)

    def test_fail_regression_not_enough_measures(self):
        native_measures = catalogue.MagnitudeMeasure.make_from_lists(
            'mb',
            [np.random.poisson(size=np.random.randint(0, 2))],
            [np.random.poisson(size=np.random.randint(0, 2))])
        target_measures = catalogue.MagnitudeMeasure.make_from_lists(
            'Mw',
            [np.random.poisson(size=np.random.randint(0, 2))],
            [np.random.poisson(size=np.random.randint(0, 2))])
        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)

        self.assertRaises(exceptions.NotEnoughSamples,
                          emsr.apply_regression_model,
                          LinearModel)

    def test_regression_with_initial_values(self):
        # Assess
        A = 0.85
        B = 1.03
        native_measures = catalogue.MagnitudeMeasure.make_from_lists(
            'mb',
            np.random.uniform(3., 8.5, 1000),
            np.random.uniform(0.02, 0.2, 1000))
        target_measures = catalogue.MagnitudeMeasure.make_from_lists(
        'Mw', A + B * np.array([m.value for m in native_measures]),
        np.random.uniform(0.025, 0.2, 1000))
        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures,
            target_measures)

        # Act
        _, output = emsr.apply_regression_model(LinearModel,
                                                initial_values=[0, 1])

        # Assert
        self.assertTrue(allclose(np.array([A, B]), output.beta))
        self.assertTrue(output.res_var < 1e-20)
