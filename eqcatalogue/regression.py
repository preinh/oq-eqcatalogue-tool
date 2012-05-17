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
Implement Regression models for Empirical Magnitude Scaling Relationship
"""

import math
from scipy import odr
import numpy as np

REGRESSOR_DEFAULT_MAX_ITERATIONS = 1000
PL_DEFAULT_INITIAL_VALUE_ORDER = 2


class RegressionFailedException(BaseException):
    def __init__(self, reason):
        super(RegressionFailedException, self).__init__(self)
        self.reason = reason

    def __repr__(self):
        return "Regression failed: %s" % self.reason


class RegressionModel(object):
    """
    The base class for a regression model

    :py:attribute:: initial_values
    The initial values used by the regression algorithm.

    :py:attribute:: akaike
    The akaike information about the performed regression

    :py:attribute:: akaike_corrected
    The normalized akaike information about the performed regression
    """

    is_regression_model = True

    def __init__(self, native_measures, target_measures,
                 initial_values=None,
                 initial_value_order=None,
                 model_params=None,
                 regressor_params=None):
        """
        Initialize a regression model

        :py:param:: native_measures
        The native measures used by regression

        :py:param:: target_measures
        The target measures used by regression

        :py:param:: initial_values
        The initial values used by regression, if None it will be
        generated from data using polyfit.

        :py:param:: initial_value_order
        The order used to calculate initial_values with polyfit

        :py:param:: model_params
        Additional parameters passed to scipy.odr.Model constructor

        :py:param:: regressor_params
        Additional parameters passed to scipy.odr.ODR constructor
        """
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
        self._output = None
        self._ndata = np.shape(native_measures.measures)[0]

    def long_str(self):
        if self.akaike_corrected:
            return "%s. AICc: %s" % (self, self.akaike_corrected)

    def func(self, x):
        return self._model_function(self._output.beta, x)

    def criterion_tests(self):
        ''' Calculate AIC and AICc'''
        nfree = float(len(self._output.beta))
        self.akaike = float(self._ndata) * \
            math.log(self._output.res_var) + 2. * nfree
        self.akaike_corrected = self.akaike + \
            (2. * nfree * (nfree + 1.)) / (float(self._ndata) - nfree - 1.)

    def run(self):
        """Perform regression analyisis"""
        self._output = self._regressor.run()

        if not 'Sum of squares convergence' in self._output.stopreason\
            and not 'Parameter convergence' in self._output.stopreason:
            # ODR Failed
            raise RegressionFailedException(self._output.stopreason)

        self.criterion_tests()

        return self._output


class PolynomialModel(RegressionModel):
    def __init__(self, native_measures, target_measures, order,
                 initial_values=None,
                 initial_value_order=None,
                 model_params=None, regressor_params=None):
        """
        Initialize a polynomial regression model.

        :py:param:: order
        The order of the polynomial used. It is used also for
        `initial_value_order` when not provided

        Look at RegressionModel#__init__ for the other parameters
        """
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
        """Use a simple least squares to get initial values. See
        RegressionModel#__init__ for a description of the
        parameters"""
        ols_data = np.polyfit(native_measures, target_measures,
                              initial_value_order)
        return np.flipud(ols_data)

    def _model_function(self, coefficients, xval):
        '''nth order polynomial function'''
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
        """Initialize a linear regression model. See
        RegressionModel#__init__ for a description of the
        parameters"""
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

    :py:attribute:: regression_models
    A dictionary where the keys are regression models objects and the
    values are the output of the regression

    :py:param:: regression_models
    An array of RegressionModel instance object storing the
    regression analysis data

    :py:param:: grouped_measures
    A list of dictionary objects. Each dictionary stores the association
    between an event (the value at key 'event') and a list of
    measures (the value at key 'measures').
    """
    DEFAULT_MODEL_TYPE = LinearModel

    @classmethod
    def make_from_events(cls, native_scale, target_scale,
                         events, selection_strategy_class,
                         **selection_strategy_args):
        """
        Build a EmpiricalMagnitudeScalingRelationship by a selecting
        measures from an event manager object according to
        a specific strategy.
        :py:param:: events
        An Event manager object.
        See EmpiricalMagnitudeScalingRelationship.make_from_measures
        for a description of other params
        """
        return cls.make_from_measures(native_scale, target_scale,
                                      events.group_measures(),
                                      selection_strategy_class,
                                      **selection_strategy_args)

    @classmethod
    def make_from_measures(cls, native_scale, target_scale,
                           grouped_measures, selection_strategy_class,
                           **selection_strategy_args):
        """
        Build a EmpiricalMagnitudeScalingRelationship by a selecting
        measures from a grouped event measure dictionary according to
        a specific strategy.
        :py:param:: native_scale
        The native scale of the EmpiricalMagnitudeScalingRelationship
        :py:param:: target_scale
        The target scale of the EmpiricalMagnitudeScalingRelationship
        :py:param:: grouped_measures
        A list of dictionary objects. Each dictionary stores the association
        between an event (the value at key 'event') and a list of
        measures (the value at key 'measures').
        :py:param:: selection_strategy_class
        A MeasureSelectionStrategy class used to select the proper measures
        :py:param:: selection_strategy_args
        Params passed to the selection_strategy_class
        """
        new_emsr = cls()
        selection_strategy = selection_strategy_class(
            **selection_strategy_args)
        native_measures, target_measures = selection_strategy.select(
            grouped_measures,
            native_scale,
            target_scale)
        new_emsr.native_measures = native_measures
        new_emsr.target_measures = target_measures
        return new_emsr

    def __init__(self, native_measures=None, target_measures=None):
        """Initialize an Empirical Magnitude Scaling Relationship instance

        :py:param:: native_measures
        A MeasureManager object holding information about the native measure
        values and their standard deviation error

        :py:param:: target_measures
        A MeasureManager object holding information about the target measure
        values and their standard deviation error
        """
        self.native_measures = native_measures
        self.target_measures = target_measures
        self.regression_models = []
        self.grouped_measures = None

    def apply_regression_model(self, model_type=DEFAULT_MODEL_TYPE,
                               **regression_params):
        """
        Apply a regression model to the measures
        :py:param:: model_type
        A RegressionModel subclass

        :py:param:: regression_params
        Arguments passed to the RegressionModel being constructed. See
        RegressionModel#__init__ documentation for details
        """
        if not hasattr(model_type, 'is_regression_model'):
            raise TypeError("Invalid Model type selected (%s). \
        It should be a subclass of RegressionModel" % model_type)
        regression_model = model_type(self.native_measures,
                                      self.target_measures,
                                      **regression_params)
        output = regression_model.run()
        self.regression_models.append(regression_model)
        return output
