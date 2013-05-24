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

from eqcatalogue.harmoniser import Harmoniser, ConversionFormula
from eqcatalogue.regression import (LinearModel,
                                    EmpiricalMagnitudeScalingRelationship)
from eqcatalogue.models import MagnitudeMeasure, CatalogueDatabase
from tests.test_filtering import load_fixtures
from eqcatalogue.filtering import C


def generate_measures():
    measures = []

    def append_fixture_measures(scale, mfactor, count=10):
        for i in range(0, count):
            measures.append(
                MagnitudeMeasure(
                    time=None,
                    position=None,
                    scale=scale,
                    value=(i + 1) * mfactor,
                    standard_error=0.2))

    # order matters!!!
    append_fixture_measures("mb", 1.0)  # from 1 to 10
    append_fixture_measures("Ml", 3.0)  # from 3 to 30
    append_fixture_measures("Mw", 2.0)  # from 2 to 20

    return measures


class HarmoniserWithFixturesAbstractTestCase(unittest.TestCase):
    """
    Create an harmonizer and some basic fixtures
    """

    def setUp(self):
        self.target_scale = "Mw"
        self.a_native_scale = "mb"
        self.ya_native_scale = "Ml"

        # generate a set of measures
        self.measures = generate_measures()
        self.number_of_measures = len(self.measures)

    def assertConversion(self, result, converted_count,
                         unconverted_count, formula_used_nr=1):
        self.assertEqual(converted_count, len(result.converted))
        self.assertEqual(unconverted_count, len(result.unconverted))

        for measure in self.measures:

            if measure in result.converted:
                converted_measure = result.converted[measure]
                if measure.scale == self.a_native_scale:
                    self.assertEqual(formula_used_nr,
                                     len(converted_measure.formulas))
                    self.assertAlmostEqual(converted_measure.value,
                                           measure.value * 2)
                elif measure.scale == self.target_scale:
                    self.assertAlmostEqual(converted_measure.value,
                                           measure.value)
                elif measure.scale == self.ya_native_scale:
                    self.assertEqual(formula_used_nr,
                                     len(converted_measure.formulas))
                    self.assertAlmostEqual(converted_measure.value,
                                           measure.value / 1.5)
            else:
                self.assertTrue(measure in result.unconverted)


class HarmoniserWithModelTestCase(HarmoniserWithFixturesAbstractTestCase):
    """
    Tests harmonization by using regression models as conversion formula
    """

    def setUp(self):
        super(HarmoniserWithModelTestCase, self).setUp()

        # mb measures
        native_measures_1 = self.measures[0:self.number_of_measures / 3]

        # Ml measures
        native_measures_2 = self.measures[
            self.number_of_measures / 3:2 * self.number_of_measures / 3]

        # Mw measures
        target_measures = self.measures[2 * self.number_of_measures / 3:]
        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures=native_measures_1,
            target_measures=target_measures)
        self.a_model, _ = emsr.apply_regression_model(LinearModel)

        emsr = EmpiricalMagnitudeScalingRelationship(
            native_measures=native_measures_2,
            target_measures=target_measures)
        self.ya_model, _ = emsr.apply_regression_model(LinearModel)

    def test_one_model(self):
        """
        Test with one model. Given a target scale, a list of measures
        (in a single magnitude scales), and an empirical magnitude
        scaling relationship (between a native scale mb and the
        considered target scale), an Harmoniser should convert to the
        target scale only the measure in that native scale
        """

        mismatches = self.number_of_measures / 3

        h = Harmoniser(target_scale=self.target_scale)
        h.add_conversion_formula_from_model(self.a_model,
                                            C(scale=self.a_native_scale))
        result = h.harmonise(self.measures)

        self.assertConversion(result, self.number_of_measures - mismatches,
                              mismatches)

    def test_no_match(self):
        """
        Test limit situations where no harmonization should happen
        """

        # model provided does not convert from the native magnitude scale
        for measure in self.measures:
            measure.scale = "fake scale"

        h = Harmoniser(target_scale=self.target_scale)
        h.add_conversion_formula_from_model(self.a_model,
                                            C(scale=self.a_native_scale))
        result = h.harmonise(self.measures)
        self.assertEqual(0, len(result.converted))
        self.assertEqual(self.number_of_measures, len(result.unconverted))

        # no model are provided
        h = Harmoniser(target_scale=self.target_scale)
        result = h.harmonise(self.measures)
        self.assertEqual(0, len(result.converted))
        self.assertEqual(self.number_of_measures, len(result.unconverted))

        # no model matches the target scale
        h = Harmoniser(target_scale="wrong scale")
        h.add_conversion_formula_from_model(self.a_model,
                                            C(scale=self.a_native_scale))
        result = h.harmonise(self.measures)
        self.assertEqual(0, len(result.converted))
        self.assertEqual(self.number_of_measures, len(result.unconverted))

    def test_more_model(self):
        h = Harmoniser(target_scale=self.target_scale)

        h.add_conversion_formula_from_model(self.a_model,
                                            C(scale=self.a_native_scale))
        h.add_conversion_formula_from_model(self.ya_model,
                                            C(scale=self.ya_native_scale))
        result = h.harmonise(self.measures)

        self.assertConversion(result, self.number_of_measures, 0)

    def test_disallow_trivial_conversion(self):
        h = Harmoniser(target_scale=self.target_scale)
        h.add_conversion_formula_from_model(self.a_model,
                                            C(scale=self.a_native_scale))
        h.add_conversion_formula_from_model(self.ya_model,
                                            C(scale=self.ya_native_scale))
        result = h.harmonise(self.measures, allow_trivial_conversion=False)

        self.assertConversion(result, 20, 10)

    def test_conversion_not_trivial_same_native_and_target_scale(self):
        h = Harmoniser(target_scale=self.target_scale)
        my_measure = self.measures[20]
        h.add_conversion_formula(
            lambda x: x * 2, 0.1, domain=C(scale="Mw"),
            target_scale="Mw")
        result = h.harmonise([my_measure], allow_trivial_conversion=False)

        self.assertEqual(1, len(result.converted))
        self.assertEqual(0, len(result.unconverted))
        self.assertAlmostEqual(my_measure.value * 2,
            result.converted[my_measure].value)


class HarmoniserWithFormulaTestCase(HarmoniserWithFixturesAbstractTestCase):
    def setUp(self):
        super(HarmoniserWithFormulaTestCase, self).setUp()
        native_measures_1 = self.measures[0:self.number_of_measures / 3]
        native_measures_2 = self.measures[
            self.number_of_measures / 3:2 * self.number_of_measures / 3]

        self.a_conversion = {'formula': lambda x: x * 2.,
                             'domain': native_measures_1,
                             'target_scale': self.target_scale,
                             'model_error': 0.1}
        self.ya_conversion = {'formula': lambda x: x / 1.5,
                              'domain': native_measures_2,
                              'target_scale': self.target_scale,
                              'model_error': 0.1}

    def test_one_conversion(self):
        """
        Test with one conversion. Given a target scale, a list of measures
        (in a single magnitude scales), and an empirical magnitude
        scaling relationship (between a native scale mb and the
        considered target scale), an Harmoniser should convert to the
        target scale only the measure in that native scale
        """

        mismatches = self.number_of_measures / 3

        h = Harmoniser(target_scale=self.target_scale)
        h.add_conversion_formula(**self.a_conversion)
        result = h.harmonise(self.measures)
        self.assertConversion(result, self.number_of_measures - mismatches,
                              mismatches)

    def test_no_match(self):
        """
        Test limit situations where no harmonization should happen
        """

        # conversion provided applies to a different domain
        h = Harmoniser(target_scale=self.target_scale)
        self.a_conversion.update({'domain': []})
        h.add_conversion_formula(**self.a_conversion)
        result = h.harmonise(self.measures)

        # 1/3 of the measures are already in the target_scale
        self.assertEqual(self.number_of_measures / 3, len(result.converted))
        self.assertEqual(self.number_of_measures * 2 / 3, len(result.unconverted))

        # no conversion are provided
        h = Harmoniser(target_scale=self.target_scale)
        result = h.harmonise(self.measures)

        self.assertEqual(self.number_of_measures / 3, len(result.converted))
        self.assertEqual(self.number_of_measures * 2 / 3,
                         len(result.unconverted))

        # no conversion matches the target scale
        h = Harmoniser(target_scale="wrong scale")
        h.add_conversion_formula(**self.a_conversion)
        result = h.harmonise(self.measures)
        self.assertEqual(0, len(result.converted))
        self.assertEqual(self.number_of_measures, len(result.unconverted))

    def test_more_conversion(self):
        """
        Test with several conversions
        """
        h = Harmoniser(target_scale=self.target_scale)

        h.add_conversion_formula(**self.a_conversion)
        h.add_conversion_formula(**self.ya_conversion)
        result = h.harmonise(self.measures)
        self.assertConversion(result, self.number_of_measures, 0)


class HarmoniserWithFormulaAndCriteriaTestCase(
        HarmoniserWithFixturesAbstractTestCase):
    """
    Test the usage of an Homogeniser by using a formula associated
    with a criteria
    """
    def setUp(self):
        super(HarmoniserWithFormulaAndCriteriaTestCase, self).setUp()
        cat = CatalogueDatabase(memory=True, drop=True)
        load_fixtures(cat.session)
        self.measures = C()

    def test_conversion(self):
        h = Harmoniser(target_scale=self.target_scale)

        h.add_conversion_formula(formula=lambda x: x * 2, model_error=0.2,
                                 domain=C(agency__in=['LDG', 'NEIC']),
                                 target_scale=self.target_scale)
        result = h.harmonise(self.measures)

        self.assertConversion(result, 6, 24)


class HarmoniserWithDifferentTargetScales(
        HarmoniserWithFixturesAbstractTestCase):
    """
    Tests the usage of an harmoniser with formula that targets
    different scales
    """

    def setUp(self):
        super(HarmoniserWithDifferentTargetScales, self).setUp()

    def test_conversion(self):
        h = Harmoniser(target_scale=self.target_scale)

        h.add_conversion_formula(formula=lambda x: x * 2., model_error=0.2,
                                 domain=C(scale=self.a_native_scale),
                                 target_scale="M2")

        h.add_conversion_formula(formula=lambda x: x * 3., model_error=0.1,
                                 domain=C(scale=self.ya_native_scale),
                                 target_scale="M3")
        h.add_conversion_formula(formula=lambda x: x * 3., model_error=0.2,
                                 domain=C(scale="M3"),
                                 target_scale="M2")
        h.add_conversion_formula(formula=lambda x: x * 4., model_error=0.3,
                                 domain=C(scale="M2"),
                                 target_scale=self.target_scale)
        h.add_conversion_formula(formula=lambda x: x * 4., model_error=0.4,
                                 domain=C(scale="M2"),
                                 target_scale="M4")
        h.add_conversion_formula(formula=lambda x: x * 4., model_error=0.2,
                                 domain=C(scale="M2"),
                                 target_scale="M5")
        result = h.harmonise(self.measures)

        self.assertEqual(30, len(result.converted))
        self.assertEqual(0, len(result.unconverted))

        for measure in self.measures:
            converted_measure = result.converted[measure]
            print measure, converted_measure
            if measure.scale == self.a_native_scale:
                self.assertAlmostEqual(
                    converted_measure.value, measure.value * 8)
            elif measure.scale == self.target_scale:
                self.assertAlmostEqual(converted_measure.value, measure.value)
            elif measure.scale == self.ya_native_scale:
                self.assertEqual(3, len(converted_measure.formulas))
                self.assertAlmostEqual(
                    converted_measure.value, measure.value * 36)


class ConversionFormulaTestCase(unittest.TestCase):

    def setUp(self):
        self.measures = generate_measures()
        self.conv_l_formula = ConversionFormula(formula=lambda x: x + 3.,
                                                model_error=0.2,
                                                domain=self.measures,
                                                target_scale="Mw")
        self.conv_p_formula = ConversionFormula(formula=lambda x: x * x + 3.,
                                                model_error=0.2,
                                                domain=self.measures,
                                                target_scale="Mw")

    def test_conversion_measures_with_defined_error(self):
        # Measure value = 1.0, Measure error = 0.2
        fst_converted_measure = self.conv_l_formula.apply(self.measures[0])
        self.assertAlmostEqual(0.28284, fst_converted_measure.standard_error,
            places=5)

        # Measure value = 18.0, Measure error = 0.2
        snd_converted_measure = self.conv_p_formula.apply(self.measures[15])
        self.assertAlmostEqual(7.20278, snd_converted_measure.standard_error,
            places=5)

    def test_conversion_measures_with_undefined_error(self):
        # Measure value = 1.0, Measure error = 0.0
        fst_measure = self.measures[0]
        fst_measure.standard_error = None

        fst_converted_measure = self.conv_l_formula.apply(fst_measure)
        self.assertAlmostEqual(0.2, fst_converted_measure.standard_error,
            places=5)

    def test_user_can_define_a_default_measure_error(self):
        # Measure value = 1.0, Measure error = 0.0
        fst_measure = self.measures[0]
        fst_measure.standard_error = None

        fst_converted_measure = self.conv_l_formula.apply(fst_measure,
            measure_uncertainty=0.4)
        self.assertAlmostEqual(0.44721, fst_converted_measure.standard_error,
            places=5)
