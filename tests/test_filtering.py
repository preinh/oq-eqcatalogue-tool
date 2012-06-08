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

from tests.test_utils import DATA_DIR, get_data_path

from eqcatalogue.importers.csv1 import CsvEqCatalogueReader, Converter
from eqcatalogue import models
from eqcatalogue.filters import EventFilter


def load_fixtures(session):
    # Allows to insert test entries in the earthquake db.
    csv_filename = get_data_path(DATA_DIR, 'query_catalogue.csv')
    with open(csv_filename) as eq_source:
        reader = CsvEqCatalogueReader(eq_source)
        entries = [entry for entry in reader.read(Converter())]

    event_source = models.EventSource(name='query_catalogue')
    session.add(event_source)
    for entry in entries:
        inserted_agency = session.query(models.Agency).filter(
                models.Agency.source_key == entry['solutionAgency'])
        if not inserted_agency.count():
            agency = models.Agency(source_key=entry['solutionAgency'],
                    eventsource=event_source)
            session.add(agency)
        else:
            agency = inserted_agency.all()[0]

        inserted_event = session.query(
                models.Event).filter_by(
                source_key=entry['eventKey'])
        if not inserted_event.count():
            event = models.Event(source_key=entry['eventKey'],
                eventsource=event_source)
            session.add(event)
        else:
            event = inserted_event.all()[0]

        entry_time = datetime(entry['year'], entry['month'], entry['day'],
                                entry['hour'], entry['minute'],
                                int(entry['second']))
        entry_pos = 'POINT(%f %f)' % (entry['Longitude'], entry['Latitude'])
        origin = models.Origin(
            time=entry_time, position=WKTSpatialElement(entry_pos),
            depth=entry['depth'], eventsource=event_source,
            source_key=entry['eventKey'])

        mag_measure = models.MagnitudeMeasure(agency=agency, event=event,
                origin=origin, scale=entry['mag_type'],
            value=entry['magnitude'])

        measure_meta = models.MeasureMetadata(
                metadata_type='stations', value=entry['stations'],
                magnitudemeasure=mag_measure)

        session.add(origin)
        session.add(mag_measure)
        session.add(measure_meta)


class AnEventFilterShould(unittest.TestCase):

    def setUp(self):
        self.cat_db = models.CatalogueDatabase(memory=True, drop=True)
        self.cat_db.recreate()
        self.event = EventFilter()
        self.session = self.cat_db.session
        load_fixtures(self.session)

    def test_allows_selection_of_all_events(self):
        self.assertEqual(5, len(self.event.all()))

    def test_allows_selection_events_on_time_criteria(self):
        time = datetime.now()
        before_time = self.event.before(time)
        after_time = self.event.after(time)
        time_lb = datetime(2001, 3, 2, 4, 11)
        time_ub = datetime(2001, 5, 2, 22, 34)
        between_time = self.event.between(time_lb, time_ub)

        self.assertEqual(30, before_time.count())
        self.assertEqual(0, after_time.count())
        self.assertEqual(6, between_time.count())

    def test_allows_selection_of_events_given_two_mag(self):
        self.assertEqual(3, len(self.event.with_magnitudes('MS', 'mb').all()))

        self.assertEqual(0, self.event.with_magnitudes('MS', 'wtf').count())

    def test_allows_selection_of_events_on_agency_basis(self):
        agency = 'LDG'
        self.assertEqual(1, len(self.event.with_agency(agency).all()))

        agency = 'NEIC'
        self.assertEqual(3, len(self.event.with_agency(agency).all()))

        agency = 'Blabla'
        self.assertEqual(0, len(self.event.with_agency(agency).all()))

        agencies = ['LDG', 'NEIC']
        self.assertEqual(3, len(self.event.with_agencies(*agencies).all()))

    def test_allows_selection_of_events_given_polygon(self):
        fst_polygon = 'POLYGON((85 35, 92 35, 92 25, 85 25, 85 35))'
        snd_polygon = 'POLYGON((92 15, 95 15, 95 10, 92 10, 92 15))'
        # Events inside first polygon: 1008566, 1008569, 1008570
        # with a sum for measures equal to 16.
        self.assertEqual(3, len(self.event.within_polygon(fst_polygon).all()))
        # Events inside second polygon: 1008567
        # with a sum for measures of 13.
        self.assertEqual(1, len(self.event.within_polygon(snd_polygon).all()))

    def test_allows_selection_of_events_given_distance_from_point(self):
        distance = 700000  # distance is expressed in meters using srid 4326
        point = 'POINT(88.20 33.10)'
        self.assertEqual(3, len(self.event.within_distance_from_point(point,
            distance).all()))

        distance = 250000
        self.assertEqual(1, len(self.event.within_distance_from_point(point,
            distance).all()))

        distance = 228000
        self.assertEqual(0, len(self.event.within_distance_from_point(point,
        distance).all()))

        distance = 2400000
        self.assertEqual(5, len(self.event.within_distance_from_point(point,
            distance).all()))

    def test_allows_grouping_of_measures(self):
        all_events = self.event
        groups = all_events.group_measures()

        self.assertEqual(5, len(groups.keys()))
        self.assertEqual(1, len(groups['1008568']))
        self.assertEqual(4, len(groups['1008570']))
        self.assertEqual(13, len(groups['1008567']))
        self.assertEqual(6, len(groups['1008569']))
        self.assertEqual(6, len(groups['1008566']))

    def tearDown(self):
        self.session.commit()
