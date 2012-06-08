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

from eqcatalogue.homogeniser import Homogeniser
from tests.test_regression import _load_catalog
from tests.test_utils import in_data_dir
from eqcatalogue.regression import LinearModel, PolynomialModel
from matplotlib.testing.compare import compare_images
from eqcatalogue import selection

ACTUAL_OUTPUT = [in_data_dir("homo%d.png" % i) for i in range(1, 14)]
EXPECTED_OUTPUT = [in_data_dir("homo%d.png" % i) for i in range(1, 14)]


class AnHomogeniserShould(unittest.TestCase):
    def setUp(self):
        _load_catalog()
        self.homogeniser = Homogeniser()
        self.homogeniser.set_scales(native="mb", target="Mw")

    def test_homogenise_easily(self):
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.add_model(PolynomialModel, order=2)

        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1],
                                       tol=4))

    def test_homogenise_different_scales(self):
        self.homogeniser.set_scales(native="Mw", target="MS")
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1],
                                       tol=4))

    def test_filter(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)

        self.assertEqual([], self.homogeniser.events())
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())

        self.homogeniser.addFilter(native_scale="MW")

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())

        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1],
                                       tol=4))

    def test_group_differently(self):
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_select_differently(self):
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual([], self.homogeniser.selectedMeasures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_1(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_2(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_3(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_4(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_5(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_6(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_7(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())

        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_8(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))

    def test_homogenise_after_different_setup_sequences_9(self):
        self.homogeniser.addFilter(agency__in="", magnitude__gt=4)
        self.homogeniser.set_grouper(
            selection.GroupMeasuresByHierarchicalClustering)
        self.homogeniser.set_selector(selection.PrecisionStrategy)

        self.assertEqual(self.homogeniser.events(), [])
        self.assertEqual([], self.homogeniser.measures())
        self.assertEqual([], self.homogeniser.grouped_measures())
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.serialize(ACTUAL_OUTPUT[1])
        self.assertTrue(
            compare_images(EXPECTED_OUTPUT[1], ACTUAL_OUTPUT[1], tol=4))
