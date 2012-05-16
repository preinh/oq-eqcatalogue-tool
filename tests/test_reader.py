# Copyright (c) 2010-2012, GEM Foundation.
#
# EqCatalogueTool is free software: you can redistribute it and/or modify it
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
# along with EqCatalogueTool. If not, see <http://www.gnu.org/licenses/>.

import unittest
from StringIO import StringIO

from eqcatalogue.reader import CsvEqCatalogueReader, Converter
from eqcatalogue.reader_utils import STR_TRANSF, INT_TRANSF, FLOAT_TRANSF


class EqCatalogueReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.fst_three_rows = StringIO(
            '1009476,1,1_IDC_ML   ,4644028,2002,9,3,21,37,37.110,1.290,0.950,'
            '25.4812,97.9598,61.5,18.6,73,0.0,,6,,156,7.0500,59.3200,4644028,'
            '3.90,0.30,1,IDC      ,ML   ,IDC' '\n'
            '1009476,1,1_IDC_mb   ,4644028,2002,9,3,21,37,37.110,1.290,0.950,'
            '25.4812,97.9598,61.5,18.6,73,0.0,,6,,156,7.0500,59.3200,4644028,'
            '3.70,0.20,3,IDC      ,mb   ,IDC' '\n'
            '1009476,1,1_IDC_mb   ,4644028,2002,9,3,21,37,37.110,1.290,0.950,'
            '25.4812,97.9598,61.5,18.6,73,0.0,,6,,156,7.0500,59.3200,4644028,'
            '3.70,0.20,3,IDC      ,mb   ,IDC')

        self.fst_exp_entry = {'azimuthGap': 156.0, 'solutionAgency': 'IDC',
                                'mag_agency': 'IDC', 'month': 9,
                                'minDistance': 7.05, 'depthError': None,
                                'second': 37.11, 'year': 2002,
                                'Latitude': 25.4812, 'time_rms': 0.95,
                                'originID': 4644028, 'phases': 6,
                                'solutionKey': 1, 'solutionDesc': '1_IDC_ML',
                                'timeError': 1.29, 'solutionID': 4644028,
                                'semiMajor90': 61.5, 'semiMinor90': 18.6,
                                'Longitude': 97.9598, 'errorAzimuth': 73.0,
                                'maxDistance': 59.32, 'day': 3, 'minute': 37,
                                'mag_type': 'ML', 'magStations': 1, 'hour': 21,
                                'stations': None, 'depth': 0.0,
                                'magnitude': 3.9, 'eventKey': 1009476,
                                'magnitudeError': 0.3}

        self.reader = CsvEqCatalogueReader(self.fst_three_rows)
        self.convert = Converter()
        self.reader_gen = self.reader.read(self.convert)
        self.maxDiff = None

    def tearDown(self):
        self.fst_three_rows.close()

    def test_read_eq_entry(self):
        first_entry = self.reader_gen.next()
        self.assertEqual(self.fst_exp_entry, first_entry)

    def test_number_generated_entries(self):
        exp_num_gen_entries = 3
        num_entries = 0
        for num_entries, _ in enumerate(self.reader_gen, start=1):
            print _
        self.assertEqual(exp_num_gen_entries, num_entries)


class ConvertTestCase(unittest.TestCase):

    def setUp(self):
        self.conversion_map = {'a': INT_TRANSF,
            'b': STR_TRANSF, 'c': FLOAT_TRANSF}
        self.converter = Converter(conversion_map=self.conversion_map)
        self.maxDiff = None

    def test_conversion_correct_values_for_keys(self):
        entry = {'a': '45', 'b': '   hazard'}
        exp_entry = {'a': 45, 'b': 'hazard'}
        self.assertEqual(exp_entry, self.converter.convert(entry))

    def test_conversion_incorrect_values_for_keys(self):
        entry = {'a': '45.78', 'b': 'risk8'}
        exp_entry = {'a': None, 'b': 'risk8'}
        self.assertEqual(exp_entry, self.converter.convert(entry))

    def test_conversion_float_and_empty_value(self):
        entry = {'b': '', 'c': '45.90'}
        exp_entry = {'b': None, 'c': 45.90}
        self.assertEqual(exp_entry, self.converter.convert(entry))
