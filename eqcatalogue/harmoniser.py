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
    def __init__(self, fn, domain, target_scale):
        self.fn = fn
        self.domain = domain
        self.target_scale = target_scale

    def is_applicable_for(self, measure):
        return measure in self.domain

    @classmethod
    def make_from_model(cls, model):
        return cls(fn=model.func, domain=model.native_measures,
                   target_scale=model.target_scale)

    def apply(self, measure):
        return self.fn(measure.value)


class Harmoniser(object):
    def __init__(self, target_scale):
        self.target_scale = target_scale
        self._formulas = {}

    def add_conversion_from_model(self, model):
        formula = ConversionFormula.make_from_model(model)
        scale = formula.target_scale
        self._formulas[scale] = self._formulas.get(scale, [])
        self._formulas[scale].append(formula)

    def harmonise(self, measures):
        converted = {}
        unconverted = []
        for m in measures:
            formula = self.find_formula_for(m)
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

    def find_formula_for(self, measure, target_scale=None):
        target_scale = target_scale or self.target_scale
        if target_scale not in self._formulas:
            return
        for formula in self._formulas[target_scale]:
            if formula.is_applicable_for(measure):
                return formula
