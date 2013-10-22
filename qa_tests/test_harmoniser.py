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
import tempfile

import eqcatalogue

from tests.test_utils import in_data_dir


class HarmoniserAPI(unittest.TestCase):
    EXPECTED_CSV_1 = """agency,event,origin,scale,value,standard_error,original_measure,formulas\r
IDC,14342462,16660453,Mw,13.5000,0.3162,"4.5 ms1mx (sigma=0.1) @ (-36.6671, -73.4847)-2010-02-28 00:00:43.000012",f1\r
IDC,17149578,16660454,Mw,12.3000,0.3162,"4.1 ms1mx (sigma=0.1) @ (-38.4963, -74.0013)-2010-02-28 00:01:46.000099",f1\r
IDC,17149583,16660459,Mw,9.9000,0.3162,"3.3 ms1mx (sigma=0.1) @ (-35.9207, -73.0304)-2010-02-28 00:35:22.000095",f1\r
IDC,14344085,16660464,Mw,10.8000,0.3162,"3.6 ms1mx (sigma=0.1) @ (-38.1626, -73.7205)-2010-02-28 00:53:30.000010",f1\r
IDC,14342120,16660469,Mw,16.5000,0.3162,"5.5 ms1mx (sigma=0.1) @ (-34.1779, -72.0708)-2010-02-28 01:08:17.000081",f1\r
NIED,14342121,17046421,Mw,5.0000,,"5.0 Mw (sigma=None) @ (25.9, 128.7)-2010-02-28 01:20:00",identity(Mw)\r
NIED,14342469,17046420,Mw,5.0000,,"5.0 Mw (sigma=None) @ (26.0, 128.8)-2010-02-28 02:51:00",identity(Mw)\r
NIED,14342473,17046419,Mw,4.9000,,"4.9 Mw (sigma=None) @ (25.9, 128.8)-2010-02-28 03:34:00",identity(Mw)\r
NIED,15626984,17046418,Mw,4.3000,,"4.3 Mw (sigma=None) @ (26.0, 128.6)-2010-02-28 04:30:00",identity(Mw)\r
NIED,14357804,17046417,Mw,4.3000,,"4.3 Mw (sigma=None) @ (26.0, 128.6)-2010-02-28 06:16:00",identity(Mw)\r
NIED,14342487,17046416,Mw,4.3000,,"4.3 Mw (sigma=None) @ (26.0, 128.6)-2010-02-28 06:54:00",identity(Mw)\r
NIED,15627037,17046415,Mw,3.9000,,"3.9 Mw (sigma=None) @ (26.0, 128.6)-2010-02-28 07:01:00",identity(Mw)\r
NIED,15627048,17046414,Mw,3.8000,,"3.8 Mw (sigma=None) @ (25.9, 128.7)-2010-02-28 07:44:00",identity(Mw)\r
NIED,14986337,17046413,Mw,5.4000,,"5.4 Mw (sigma=None) @ (34.8, 142.1)-2010-02-28 08:17:00",identity(Mw)\r
NIED,14342500,17046412,Mw,4.5000,,"4.5 Mw (sigma=None) @ (26.4, 128.6)-2010-02-28 10:32:00",identity(Mw)\r
NIED,14357813,17046411,Mw,4.0000,,"4.0 Mw (sigma=None) @ (34.8, 142.2)-2010-02-28 13:51:00",identity(Mw)\r
NIED,15627159,17046410,Mw,4.1000,,"4.1 Mw (sigma=None) @ (26.1, 128.8)-2010-02-28 15:09:00",identity(Mw)\r
NIED,14869776,17046409,Mw,3.8000,,"3.8 Mw (sigma=None) @ (25.9, 128.7)-2010-02-28 18:36:00",identity(Mw)\r
NIED,14342524,17046408,Mw,5.1000,,"5.1 Mw (sigma=None) @ (39.4, 140.7)-2010-02-28 22:08:00",identity(Mw)\r
"""

    EXPECTED_CSV_2 = """agency,event,origin,scale,value,standard_error,original_measure,formulas\r
ISCJB,14342462,00698814,Mw,46.8000,0.3162,"5.2 MS (sigma=None) @ (-36.5503, -73.2)-2010-02-28 00:00:46.000048",f2.f4\r
ISCJB,14344085,00698822,Mw,45.9000,0.3162,"5.1 MS (sigma=None) @ (-38.0951, -73.5244)-2010-02-28 00:53:29.000030",f2.f4\r
ISCJB,14357799,00698823,Mw,46.8000,0.3162,"5.2 MS (sigma=None) @ (-36.7981, -73.2883)-2010-02-28 01:01:09.000034",f2.f4\r
ISCJB,14342120,00698827,Mw,51.3000,0.3162,"5.7 MS (sigma=None) @ (-34.1789, -71.9601)-2010-02-28 01:08:23.000009",f2.f4\r
ISCJB,17149591,00698831,Mw,46.8000,0.3162,"5.2 MS (sigma=None) @ (-37.0751, -73.4898)-2010-02-28 01:14:44.000031",f2.f4\r
ISCJB,14342121,00698833,Mw,45.9000,0.3162,"5.1 MS (sigma=None) @ (25.9621, 128.4732)-2010-02-28 01:20:30.000029",f2.f4\r
ISCJB,14342464,00698837,Mw,46.8000,0.3162,"5.2 MS (sigma=None) @ (-36.5613, -72.5948)-2010-02-28 01:33:11.000047",f2.f4\r
ISCJB,14986337,00698960,Mw,47.7000,0.3162,"5.3 MS (sigma=None) @ (34.7853, 141.536)-2010-02-28 08:17:44.000054",f2.f4\r
ISCJB,14357818,00699132,Mw,51.3000,0.3162,"5.7 MS (sigma=None) @ (-38.0121, -73.5057)-2010-02-28 19:48:37",f2.f4\r
"""

    EXPECTED_CSV_3 = """agency,event,origin,scale,value,standard_error,original_measure,formulas\r
IDC,14357800,16660466,Mw,12.6000,0.6083,"4.3 mb1 (sigma=0.1) @ (38.1742, 71.6013)-2010-02-28 01:01:30.000091",f5.f6\r
IDC,14357810,16660683,Mw,11.4000,0.6083,"4.1 mb1 (sigma=0.1) @ (35.5966, 71.3818)-2010-02-28 11:45:38.000028",f5.f6\r
IDC,17149741,16660686,Mw,8.4000,0.6083,"3.6 mb1 (sigma=0.1) @ (27.9507, 81.5725)-2010-02-28 11:54:40.000061",f5.f6\r
IDC,14344132,16660712,Mw,10.8000,0.6083,"4.0 mb1 (sigma=0.1) @ (37.2171, 72.3773)-2010-02-28 13:31:09.000003",f5.f6\r
IDC,16248642,16660851,Mw,10.8000,0.6083,"4.0 mb1 (sigma=0.1) @ (28.353, 86.5692)-2010-02-28 22:03:18.000081",f5.f6\r
"""

    def setUp(self):
        eqcatalogue.CatalogueDatabase(filename=in_data_dir('qa.db'))
        self.maxDiff = None

    def test_harmonise_with_one_custom_formula(self):
        csv_file = tempfile.NamedTemporaryFile()

        h = eqcatalogue.Harmoniser("Mw")

        h.add_conversion_formula(lambda m: m * 3., 0.1,
                                 domain=eqcatalogue.C(scale="ms1mx")[0:5],
                                 target_scale="Mw",
                                 name="f1")

        h.harmonise(eqcatalogue.C()).export(filename=csv_file.name)

        self.assertEqual(self.EXPECTED_CSV_1, csv_file.read())

    def test_harmonise_with_three_custom_formula(self):
        csv_file = tempfile.NamedTemporaryFile()

        h = eqcatalogue.Harmoniser("Mw")

        h.add_conversion_formula(lambda m: m * 3., 0.1,
                                 domain=eqcatalogue.C(
                                     scale="MS", agency='ISCJB',
                                     magnitude__gt=5),
                                 target_scale="M1",
                                 name="f2")

        h.add_conversion_formula(lambda m: m * 3., 0.1,
                                 domain=eqcatalogue.C(scale="ms1x"),
                                 target_scale="Mw",
                                 name="f3")

        h.add_conversion_formula(lambda m: m * 3., 0.1,
                                 domain=eqcatalogue.C(scale='M1'),
                                 target_scale="Mw",
                                 name="f4")

        result = h.harmonise(eqcatalogue.C(), allow_trivial_conversion=False)

        result.export(filename=csv_file.name)

        self.assertEqual(self.EXPECTED_CSV_2, csv_file.read())

    def test_harmonise_with_a_formula_and_a_regression(self):
        csv_file = tempfile.NamedTemporaryFile()

        h = eqcatalogue.Harmoniser("Mw")

        homogeniser = eqcatalogue.Homogeniser(
            native_scale="mb1", target_scale="ML",
            criteria=eqcatalogue.C(
                within_distance_from_point=["POINT(-34 -70)", 100000]),
            missing_uncertainty_strategy=eqcatalogue.MUSSetDefault(0.5))
        homogeniser.add_model(eqcatalogue.LinearModel)

        model = homogeniser.perform_regression()[0]['model']

        h.add_conversion_formula_from_model(model,
                                            eqcatalogue.C(scale='mb1'),
                                            name="f5")

        h.add_conversion_formula(lambda m: m * 3., 0.1,
                                 domain=eqcatalogue.C(scale="ML"),
                                 target_scale="Mw",
                                 name="f6")

        h.harmonise(eqcatalogue.C(
            scale='mb1',
            within_distance_from_point=['POINT(28 80)', 1000000])).export(
                filename=csv_file.name)

        self.assertEqual(self.EXPECTED_CSV_3, csv_file.read())
