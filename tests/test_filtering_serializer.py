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

import tempfile
import unittest
from eqcatalogue import filtering
from eqcatalogue.serializers import csv_export

from tests import test_utils


class ShouldExportMeasures(unittest.TestCase):
    EXPECTED_CSV_1 = """id,agency,event,origin,scale,value,standard_error\r
18,ISC,14342462,00198763,MS,5.2,0.1\r
19,ISC,14342462,00198763,mb,5.3,0.2\r
36,ISC,14344085,00198775,MS,5.1,0.1\r
37,ISC,14344085,00198775,mb,5.1,0.1\r
51,ISC,14357799,00198776,mb,5.3,0.1\r
74,ISC,14342120,00198780,MS,5.8,0.1\r
75,ISC,14342120,00198780,mb,5.5,0.2\r
91,ISC,14342464,00198792,MS,5.2,0.6\r
92,ISC,14342464,00198792,mb,5.3,0.2\r
"""

    def setUp(self):
        test_utils.load_catalog()

    def test_csv_serializers(self):
        csv_file = tempfile.NamedTemporaryFile()
        measures = filtering.C(agency__in=['ISC'])[0:9]

        csv_export.measures(measures, filename=csv_file.name)
        self.assertEqual(self.EXPECTED_CSV_1, csv_file.read())
