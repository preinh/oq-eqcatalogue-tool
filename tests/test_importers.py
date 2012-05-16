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
from eqcatalogue.importers import isf_bulletin as isf
from eqcatalogue import models as catalogue
from tests.test_utils import in_data_dir


# the following data has been downloaded by issuing the
# following command
# query_isc_catalogue(cat, start_year=2010, start_month=2,
# start_day=28, end_year=2010, end_month=3, end_day=01)

DATAFILE = in_data_dir('isc_query_1.html')


class ShouldImportFromISFBulletinV1(unittest.TestCase):

    def test_detect_junk_lines(self):
        # Assess
        f = file(DATAFILE)
        cat = catalogue.CatalogueDatabase(memory=True, drop=True)

        # Act
        importer = isf.V1(f, cat)

        # Assert
        self.assertRaises(isf.UnexpectedLine, importer.load, (False))

        f.close()

    def test_parse_html_file(self):
        # Assess
        f = file(DATAFILE)
        cat = catalogue.CatalogueDatabase(memory=True, drop=True)

        # Act
        summary = isf.V1.import_events(f, cat)

        # Assert
        self.assertEqual(summary, {
                    'eventsource_created': 1,
                    'agency_created': 75,
                    'event_created': 1254,
                    'origin_created': 2770,
                    'measure_created':  5091,
                    })

        sources = cat.session.query(catalogue.EventSource)
        agencies = cat.session.query(catalogue.Agency)
        events = cat.session.query(catalogue.Event)
        origins = cat.session.query(catalogue.Origin)
        measures = cat.session.query(catalogue.MagnitudeMeasure)

        self.assertEqual(sources.count(),  1)
        self.assertEqual(agencies.count(),  75)
        self.assertEqual(events.count(),  1254)
        self.assertEqual(origins.count(),  2770)
        self.assertEqual(measures.count(),  5091)

        f.close()
