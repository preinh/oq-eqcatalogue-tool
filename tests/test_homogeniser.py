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
from os import path
from eqcatalogue.homogeniser import Homogeniser
from tests.test_utils import _load_catalog
from tests.test_utils import in_data_dir
from eqcatalogue.regression import LinearModel, PolynomialModel
from eqcatalogue import selection, grouping, models

ACTUAL_OUTPUT = [in_data_dir("actual_homo%d.png" % i)
                 for i in range(1, 14)]


class AnHomogeniserShould(unittest.TestCase):
    def setUp(self):
        _load_catalog()
        self.homogeniser = Homogeniser()
        self.homogeniser.set_scales(native="mb", target="MS")
        self.i = 0

    def _write_and_check(self):
        self.homogeniser.serialize(ACTUAL_OUTPUT[self.i])
        self.assertTrue(path.exists(in_data_dir(ACTUAL_OUTPUT[self.i])))
        self.i = self.i + 1

    def test_homogenise_easily(self):
        self.homogeniser.add_model(LinearModel)
        self.homogeniser.add_model(PolynomialModel, order=2)

        self._write_and_check()

    def test_homogenise_different_scales(self):
        self.homogeniser.reset_filters()
        self.homogeniser.set_scales(native="mb", target="MS")
        self.homogeniser.set_missing_uncertainty_strategy(
            selection.MUSSetDefault, default=0.2)
        self.homogeniser.add_model(LinearModel)
        self._write_and_check()

    def test_filter(self):
        self.homogeniser.add_filter(agency__in=["ISC", "GCMT"],
                                    magnitude__gt=5.5)

        self.assertEqual([
            "Event 14342462 from EventSource ISC Bulletin",
            "Event 14357799 from EventSource ISC Bulletin",
            "Event 14342120 from EventSource ISC Bulletin",
            "Event 14342464 from EventSource ISC Bulletin",
            "Event 14342123 from EventSource ISC Bulletin",
            "Event 14986337 from EventSource ISC Bulletin",
            "Event 14342499 from EventSource ISC Bulletin",
            "Event 17273456 from EventSource ISC Bulletin",
            "Event 14342516 from EventSource ISC Bulletin",
            "Event 14342520 from EventSource ISC Bulletin",
            "Event 14357818 from EventSource ISC Bulletin"],
            [str(e) for e in self.homogeniser.events()])

        self.assertEqual(53, len(self.homogeniser.measures()))

        self.assertEqual([u'14342464', u'14986337',
                          u'14342462', u'14357799',
                          u'14357818', u'14342516',
                          u'14342123', u'17273456',
                          u'14342120', u'14342499',
                          u'14342520'],
                         self.homogeniser.grouped_measures().keys())

        self.homogeniser.add_filter(scale__in=["Mw", "mb"])
        self.assertEqual(17, len(self.homogeniser.events()))
        self.assertEqual(97, len(self.homogeniser.measures()))
        self.assertEqual(17, len(self.homogeniser.grouped_measures().keys()))
        self.assertEqual(0, len(self.homogeniser.selected_native_measures()))

    def test_set_different_mus(self):
        self.homogeniser.set_scales(native="mb", target="Mw")
        self.assertEqual(18, len(self.homogeniser.events()))
        self.assertEqual(334, len(self.homogeniser.measures()))
        self.assertEqual(18, len(self.homogeniser.grouped_measures().keys()))
        self.assertEqual(0, len(self.homogeniser.selected_native_measures()))

        self.homogeniser.set_missing_uncertainty_strategy(
            selection.MUSSetDefault, default=1)

        self.assertEqual(18, len(self.homogeniser.events()))
        self.assertEqual(334, len(self.homogeniser.measures()))
        self.assertEqual(18, len(self.homogeniser.grouped_measures().keys()))
        self.assertEqual(1, len(self.homogeniser.selected_native_measures()))

    def test_group_differently(self):
        self.assertEqual(18, len(self.homogeniser.grouped_measures().keys()))
        self.homogeniser.set_grouper(
            grouping.GroupMeasuresByHierarchicalClustering,
            args={'t': 1000})
        self.assertEqual(14, len(self.homogeniser.grouped_measures().keys()))

    def test_select_differently(self):
        self.assertEqual(14, len(self.homogeniser.selected_native_measures()))
        self.homogeniser.set_selector(selection.Precise)
        self.assertEqual(14, len(self.homogeniser.selected_native_measures()))

    def test_homogenise_after_different_setup_sequences_1(self):
        self.homogeniser.set_scales(native="MS", target="MW")
        self.homogeniser.add_filter(magnitude__gt=4)
        self.homogeniser.set_grouper(
            grouping.GroupMeasuresByHierarchicalClustering,
            args={'t': 100})
        self.homogeniser.set_selector(selection.Precise)
        self.homogeniser.set_missing_uncertainty_strategy(
            selection.MUSSetDefault, default=1)

        self.assertTrue(len(self.homogeniser.selected_native_measures()) > 1)
        self.assertTrue(len(self.homogeniser.selected_target_measures()) > 1)

        self.homogeniser.add_model(LinearModel)
        self._write_and_check()

    def test_homogenise_after_different_setup_sequences_2(self):
        self.homogeniser.set_scales(native="MS", target="MW")
        self.homogeniser.set_grouper(
            grouping.GroupMeasuresByHierarchicalClustering,
            args={'t': 100})
        self.homogeniser.add_filter(magnitude__gt=4)
        self.homogeniser.set_selector(selection.Precise)
        self.homogeniser.set_missing_uncertainty_strategy(
            selection.MUSSetDefault, default=1)

        self.assertTrue(len(self.homogeniser.selected_native_measures()) > 1)
        self.assertTrue(len(self.homogeniser.selected_target_measures()) > 1)

        self.homogeniser.add_model(LinearModel)
        self._write_and_check()

    def tearDown(self):
        models.CatalogueDatabase().session.commit()
