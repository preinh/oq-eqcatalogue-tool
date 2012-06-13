# Copyright (c) 2010-2012, GEM Foundation.
#
# eqcataloguetool is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EqCatalogueTool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with eqcataloguetool. If not, see <http://www.gnu.org/licenses/>.

"""
Module :mod:`eqcatalogue.regressions` defines
:class:`RegressionModel`, :class:`LinearModel`, :class:`PolynomialModel`,
:class:`EmpiricalMagnitudeScalingRelationship`.
"""

import math
from scipy import odr
import numpy as np
from eqcatalogue import selection
from eqcatalogue import exceptions


REGRESSOR_DEFAULT_MAX_ITERATIONS = 3000
PL_DEFAULT_INITIAL_VALUE_ORDER = 2


class RegressionModel(object):
    """
    The base class for a regression model

    :output: the scipy output of the regression

    :param native_measures:
        The native measures used by regression

    :param target_measures:
        The target measures used by regression

    :param initial_values:
        The initial values used by regression, if None it will be
        generated from data using polyfit.

    :param initial_value_order:
        The order used to calculate initial_values with polyfit

    :param model_params:
        Additional parameters passed to scipy.odr.Model constructor

    :param regressor_params:
        Additional parameters passed to scipy.odr.ODR constructor

    :attribute intial_values: the initial values used by the regression
        algorithm.

    :attribute akaike: akaike information about the performed regression.
        The akaike number gives you a measure of the goodness of fit of the
        regression model.

    :attribute akaike_corrected: The normalized akaike information about
        the performed regression suitable for finite sample sizes
    """

    is_regression_model = True

    def __init__(self, native_measures, target_measures,
                 initial_values=None,
                 initial_value_order=None,
                 model_params=None,
                 regressor_params=None):

        if not initial_values:
            self.initial_values = self._setup_initial_values(
                native_measures.measures,
                target_measures.measures,
                initial_value_order)
        else:
            self.initial_values = initial_values
        actual_model_params = {}
        if model_params:
            actual_model_params.update(model_params)
        self._regression_model = odr.Model(self._model_function,
                                           **actual_model_params)
        self._regression_data = odr.RealData(native_measures.measures,
                                             target_measures.measures,
                                             sx=native_measures.sigma,
                                             sy=target_measures.sigma)
        actual_regressor_params = {'maxit': REGRESSOR_DEFAULT_MAX_ITERATIONS}
        if regressor_params:
            actual_regressor_params.update(regressor_params)

        self._regressor = odr.ODR(self._regression_data,
                                  self._regression_model,
                                  beta0=self.initial_values,
                                  **actual_regressor_params)
        self.akaike = None
        self.akaike_corrected = None
        self.output = None
        self.sample_size = float(np.shape(native_measures.measures)[0])

    def long_str(self):
        return "%s. AICc: %s" % (self, self.akaike_corrected)

    def func(self, x):
        return self._model_function(self.output.beta, x)

    def parameter_number(self):
        """Returns the number of parameters of the regression model"""
        return float(len(self.output.beta))

    def residual(self):
        return self.output.res_var

    def criterion_tests(self):
        """
        Calculate AIC and AICc
        """

        # number of parameters of the model
        nfree = self.parameter_number()

        self.akaike = float(self.sample_size) * \
            math.log(self.residual()) + 2. * nfree
        self.akaike_corrected = self.akaike + \
            (2. * nfree * (nfree + 1.)) / (self.sample_size - nfree - 1.)

    def run(self):
        """Perform regression analyisis"""

        self.output = self._regressor.run()

        if not 'Sum of squares convergence' in self.output.stopreason\
            and not 'Parameter convergence' in self.output.stopreason:
            # ODR Failed
            raise exceptions.RegressionFailedException(
                "Regression failed: %s" % self.output.stopreason)

        self.criterion_tests()

        return self.output


class PolynomialModel(RegressionModel):
    """
    Initialize a polynomial regression model.

    :param order: The order of the polynomial used. It is used also for
        `initial_value_order` when not provided
    """

    def __init__(self, native_measures, target_measures, order,
                 initial_values=None,
                 initial_value_order=None,
                 model_params=None, regressor_params=None):

        if not order:
            raise ValueError("Please specify the polynomial order")
        self._order = order
        super(PolynomialModel, self).__init__(native_measures,
                                              target_measures,
                                              initial_values,
        # we setup the order of the polynomial used by OLS to setup
        # the initial_values equal to the order of the polynomial
        # model function
                                              initial_value_order or order,
                                              model_params, regressor_params)

    def __str__(self):
        return "Polynomial Model of order %d" % self._order

    def _setup_initial_values(self, native_measures, target_measures,
                              initial_value_order):
        """
        Use a simple least squares to get initial values. See
        RegressionModel#__init__ for a description of the
        parameters
        """

        ols_data = np.polyfit(native_measures, target_measures,
                              initial_value_order)
        return np.flipud(ols_data)

    def _model_function(self, coefficients, xval):
        """nth order polynomial function"""

        yval = 0.
        for iloc, param in enumerate(coefficients):
            yval = yval + param * (xval ** float(iloc))
        return yval


class LinearModel(PolynomialModel):
    def __init__(self, native_measures, target_measures,
                 initial_values=None,
                 initial_value_order=None,
                 model_params=None,
                 regressor_params=None):
        super(LinearModel, self).__init__(native_measures,
                                          target_measures,
                                          1,  # polynomial order
                                          initial_values,
                                          initial_value_order,
                                          model_params, regressor_params)

    def __str__(self):
        return "Linear Model"


class EmpiricalMagnitudeScalingRelationship(object):
    """
    Decribes an Empirical Magnitude Scaling Relationship

    :attribute regression_models:
        A dictionary where the keys are regression models objects and the
        values are the output of the regression.

    :attribute grouped_measures:
        A dictionary that stores the association between an event (the key)
        and a list of measures (the value).

    :param regression_models:
        An array of RegressionModel instance object storing the
        regression analysis data.

    :param native_measures:
        A :class:`~eqcatalogue.selection.MeasureManager` instance holding
        information about the native measure values and their standard
        deviation error.

    :param target_measures:
        A :class:`~eqcatalogue.selection.MeasureManager` instance holding
        information about the target measure values and their standard
        deviation error.
    """

    DEFAULT_MODEL_TYPE = LinearModel

    @classmethod
    def make_from_events(cls, native_scale, target_scale,
                         events, selection_strategy,
                         missing_uncertainty_strategy=None):
        """
        Build a EmpiricalMagnitudeScalingRelationship by a selecting
        measures from an event manager object according to
        a specific strategy.

        :param native_scale: The native scale of the
            EmpiricalMagnitudeScalingRelationship.

        :param target_scale: The target scale of the
            EmpiricalMagnitudeScalingRelationship.

        :param events: A :class:`~eqcatalogue.filtering.MeasureFilter`
            instance.

        :param selection_strategy:
            A :class:`~eqcatalogue.selection.MeasureSelection` instance.

        :param missing_uncertainty_strategy:
            A :class:`~eqcatalogue.selection.MissingUncertaintyStrategy`
            instance.
        """

        return cls.make_from_measures(native_scale, target_scale,
                                      events.group_measures(),
                                      selection_strategy,
                                      missing_uncertainty_strategy)

    @classmethod
    def make_from_measures(cls, native_scale, target_scale,
                           grouped_measures, selection_strategy,
                           missing_uncertainty_strategy=None):
        """
        Build a EmpiricalMagnitudeScalingRelationship by a selecting
        measures from a grouped event measure dictionary according to
        a specific strategy.

        :param native_scale: The native scale of the
            EmpiricalMagnitudeScalingRelationship.

        :param target_scale: The target scale of the
            EmpiricalMagnitudeScalingRelationship.

        :param grouped_measures:
            A dictionary that stores the association
            between an event (the key) and a list of
            measures (the value).

        :param selection_strategy:
            A :class:`~eqcatalogue.selection.MeasureSelection` instance.

        :param missing_uncertainty_strategy:
            A :class:`~eqcatalogue.selection.MissingUncertaintyStrategy`
            instance.
        """

        new_emsr = cls()
        native_measures, target_measures = selection_strategy.select(
            grouped_measures,
            native_scale,
            target_scale,
            missing_uncertainty_strategy or selection.MUSDiscard())
        new_emsr.native_measures = native_measures
        new_emsr.target_measures = target_measures
        return new_emsr

    def __init__(self, native_measures=None, target_measures=None):
        self.native_measures = native_measures
        self.target_measures = target_measures
        self.regression_models = []
        self.grouped_measures = None

    def apply_regression_model(self, model_type=DEFAULT_MODEL_TYPE,
                               **regression_params):
        """
        Apply a regression model to the measures
        :param model_type:
            an instance of :class:`~eqcatalgue.regression.RegressionModel`.

        :param regression_params:
            Arguments passed to the RegressionModel being constructed. See
            RegressionModel#__init__ documentation for details.

        :return:
            a tuple with a RegressionModel instance and its output
        """
        if not hasattr(model_type, 'is_regression_model'):
            raise TypeError("Invalid Model type selected (%s). \
        It should be a subclass of RegressionModel" % model_type)

        if len(self.native_measures) < 3:
            raise exceptions.NotEnoughSamples(
                "Not enough measures to perform regression. "
                "Please relax your query or selection criteria")

        regression_model = model_type(self.native_measures,
                                      self.target_measures,
                                      **regression_params)
        output = regression_model.run()
        self.regression_models.append(regression_model)
        return regression_model, output
