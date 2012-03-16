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

from oq_eqcatalogue_tool.reader import EqCatalogueReader, Convert



class EqCatalogueReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.fst_row_values = StringIO(
            '1009476,1,1_IDC_ML   ,4644028,2002,9,3,21,37,37.110,1.290,0.950,'
            '25.4812,97.9598,61.5,18.6,73,0.0,,6,,156,7.0500,59.3200,4644028,'
            '3.90,0.30,1,IDC      ,ML   ,IDC')

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

        self.reader = EqCatalogueReader(self.fst_row_values)
        self.convert = Convert()

    def test_read_eq_entry(self):
        reader_gen = self.reader.read(self.convert)
        first_entry = reader_gen.next()
        self.assertEqual(self.fst_exp_entry, first_entry)
