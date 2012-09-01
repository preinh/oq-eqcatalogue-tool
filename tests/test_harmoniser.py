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

from eqcatalogue.harmoniser import Harmoniser
from eqcatalogue.regression import (LinearModel,
                                    EmpiricalMagnitudeScalingRelationship)
from eqcatalogue.models import MagnitudeMeasure, Event


class HarmoniserWithModelTestCase(unittest.TestCase):

    def setUp(self):
        self.target_scale = "Mw"
        self.a_native_scale = "mb"
        self.ya_native_scale = "Ml"

        # generate a set of measures
        self.measures = []

        events = [Event(source_key=i, eventsource=None,
                  name="test event %d" % i) for i in range(0, 10)]

        for i in range(0, 10):
            self.measures.append(
                MagnitudeMeasure(
                    agency=None, event=events[i], origin=None,
                    scale=self.a_native_scale,
                    standard_error=1, value=(i + 1) * 1.0))

        for i in range(0, 10):
            self.measures.append(
                MagnitudeMeasure(
                    agency=None, event=events[i], origin=None,
                    scale=self.ya_native_scale,
                    standard_error=1, value=(i + 1) * 3.0))

        for i in range(0, 10):
            self.measures.append(
                MagnitudeMeasure(
                    agency=None, event=events[i], origin=None,
                    scale=self.target_scale,
                    standard_error=1, value=(i + 1) * 2.0))

        self.number_of_measures = len(self.measures)
        native_measures_1 = self.measures[0:self.number_of_measures / 3]
        native_measures_2 = self.measures[
            self.number_of_measures / 3:2 * self.number_of_measures / 3]
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
        h.add_conversion_from_model(self.a_model)
        converted, unconverted = h.harmonise(self.measures)

        self.assertEqual(self.number_of_measures - mismatches,
                         len(converted))
        self.assertEqual(len(unconverted), mismatches)
        for measure in self.measures:
            if measure in converted:
                converted_measure = converted[measure]
                if measure.scale == self.a_native_scale:
                    self.assertEqual(1, len(converted_measure['formulas']))
                    self.assertAlmostEqual(converted_measure['value'],
                                           measure.value * 2)
                elif measure.scale == self.target_scale:
                    self.assertEqual(converted_measure['formulas'], [])
                    self.assertAlmostEqual(converted_measure['value'],
                                           measure.value)

    def test_no_match(self):
        """
        Test limit situations where no harmonization should happen
        """

        # model provided does not convert from the native magnitude scale
        for measure in self.measures:
            measure.scale = "fake scale"

        h = Harmoniser(target_scale=self.target_scale)
        h.add_conversion_from_model(self.a_model)
        converted, unconverted = h.harmonise(self.measures)
        self.assertEqual(0, len(converted))
        self.assertEqual(self.number_of_measures, len(unconverted))

        # no model are provided
        h = Harmoniser(target_scale=self.target_scale)
        converted, unconverted = h.harmonise(self.measures)
        self.assertEqual(0, len(converted))
        self.assertEqual(self.number_of_measures, len(unconverted))

        # no model matches the target scale
        h = Harmoniser(target_scale="wrong scale")
        h.add_conversion_from_model(self.a_model)
        converted, unconverted = h.harmonise(self.measures)
        self.assertEqual(0, len(converted))
        self.assertEqual(self.number_of_measures, len(unconverted))

    def test_more_model(self):
        """
        Test with several models
        """
        h = Harmoniser(target_scale=self.target_scale)

        h.add_conversion_from_model(self.a_model)
        h.add_conversion_from_model(self.ya_model)
        converted, unconverted = h.harmonise(self.measures)

        self.assertEqual(0, len(unconverted))
        self.assertEqual(self.number_of_measures, len(converted))

        for measure in self.measures:
            converted_measure = converted[measure]
            if measure.scale == self.a_native_scale:
                self.assertEqual(1, len(converted_measure['formulas']))
                self.assertAlmostEqual(converted_measure['value'],
                                       measure.value * 2)
            elif measure.scale == self.target_scale:
                self.assertEqual(0, len(converted_measure['formulas']))
                self.assertAlmostEqual(converted_measure['value'],
                                       measure.value)
            elif measure.scale == self.ya_native_scale:
                self.assertEqual(1, len(converted_measure['formulas']))
                self.assertAlmostEqual(converted_measure['value'],
                                       measure.value / 1.5)
