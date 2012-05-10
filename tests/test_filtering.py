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
from datetime import datetime
from geoalchemy import WKTSpatialElement

from tests.utils import DATA_DIR, get_data_path

from eqcatalogue.reader import CsvEqCatalogueReader, Converter
from eqcatalogue import models as catalogue


def load_fixtures(session):
    csv_filename = get_data_path(DATA_DIR, 'query_catalogue.csv')
    with open(csv_filename) as eq_source:
        reader = CsvEqCatalogueReader(eq_source)
        entries = [entry for entry in reader.read(Converter())]

    event_source = catalogue.EventSource(name='query_catalogue')
    session.add(event_source)
    for entry in entries:
        inserted_agency = session.query(
                catalogue.Agency).filter_by(
                name=entry['solutionAgency']).count()
        if not inserted_agency:
            agency = catalogue.Agency(source_key=entry['eventKey'],
                    eventsource=event_source,
                    name=entry['solutionAgency'])
            session.add(agency)

        event = catalogue.Event(source_key=entry['eventKey'],
                eventsource=event_source)

        entry_time = datetime(entry['year'], entry['month'], entry['day'],
                                entry['hour'], entry['minute'],
                                int(entry['second']))
        entry_pos = 'POINT(%f %f)' % (entry['Longitude'], entry['Latitude'])
        origin = catalogue.Origin(
            time=entry_time, position=WKTSpatialElement(entry_pos),
            depth=entry['depth'], eventsource=event_source,
            source_key=entry['eventKey'])

        mag_measure = catalogue.MagnitudeMeasure(agency=agency, event=event,
                origin=origin, scale=entry['mag_type'],
            value=entry['magnitude'])

        measure_meta = catalogue.MeasureMetadata(
                metadata_type='stations', value=entry['stations'],
                magnitudemeasure=mag_measure)

        session.add(event)
        session.add(origin)
        session.add(mag_measure)
        session.add(measure_meta)


class AnEqCatalogueShould(unittest.TestCase):

    def setUp(self):
        cat_db = catalogue.CatalogueDatabase(memory=False, drop=True)
        self.session = cat_db.session
        load_fixtures(self.session)

    def test_p(self):
        self.assertTrue(True)

    def tearDown(self):
        self.session.commit()
