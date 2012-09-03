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

"""
This module provides the main class that handles the harmonisation
of a set of measures to a single target scale
"""


class ConversionFormula(object):
    """
    An object holding a formula that can convert a measure into a
    target magnitude scale

    :attribute formula:
      A callable that accepts one argument that holds the measure value
      to be converted

    :attribute domain:
      A list of measures that stores exhaustively the domain of the
      formula

    :attribute target_scale
      The target scale
    """
    def __init__(self, formula, domain, target_scale):
        self.formula = formula
        self.domain = domain
        self.target_scale = target_scale

    def is_applicable_for(self, measure):
        """Returns true if the measure given in input can be converted"""
        return measure in self.domain

    @classmethod
    def make_from_model(cls, model):
        """
        Build a conversion model by a regression model
        """
        return cls(formula=model.func, domain=model.native_measures,
                   target_scale=model.target_scale)

    def apply(self, measure):
        """
        Apply the conversion to `measure`. Raise an error if the
        `measure` does not belong to the domain of the conversion
        formula
        """
        if not self.is_applicable_for(measure):
            raise ValueError(
                "You can not apply the conversion to this measure")
        return self.formula(measure.value)


class Harmoniser(object):
    """
    This class is responsable to convert a set of measures into a
    target scale by using a set of conversion formula

    :attribute target_scale
      The target scale considered

    :attribute _formulas
      The list of formulas used to convert measures
    """
    def __init__(self, target_scale):
        self.target_scale = target_scale
        self._formulas = {}

    def add_conversion(self, formula, domain, target_scale):
        formula = ConversionFormula(formula, domain, target_scale)
        self._add_formula(formula)

    def add_conversion_from_model(self, model):
        """
        Create a conversion formula from a regression model and make
        it available for the harmonizer

        :param model
          A regression model
        """
        formula = ConversionFormula.make_from_model(model)
        self._add_formula(formula)

    def _add_formula(self, formula):
        scale = formula.target_scale
        self._formulas[scale] = self._formulas.get(scale, [])
        self._formulas[scale].append(formula)

    def harmonise(self, measures):
        """
        Harmonize an iterator of measures.

        :param measures
          the measures to be converted

        :return the converted and the unconverted measures
        :rtype a 2-tuple. The former is dictionary where the keys are
        the converted measures and the value is a dictionary storing
        the converted value and the formula used for the conversion.
        The latter is a list of the unconverted measures
        """
        converted = {}
        unconverted = []
        for m in measures:
            formula = self._find_formula_for(m)
            if formula:
                converted[m] = dict(
                    value=formula.apply(m),
                    formulas=[formula])
            elif m.scale == self.target_scale:
                converted[m] = dict(
                    value=m.value,
                    formulas=[])
            else:
                unconverted.append(m)
        return converted, unconverted

    def _find_formula_for(self, measure, target_scale=None):
        """
        Find a formula to convert `measure` to `target_scale`
        """
        target_scale = target_scale or self.target_scale
        if target_scale not in self._formulas:
            return
        for formula in self._formulas[target_scale]:
            if formula.is_applicable_for(measure):
                return formula
