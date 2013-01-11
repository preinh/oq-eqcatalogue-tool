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

from datetime import datetime
import unittest
from eqcatalogue import models as catalogue
import geoalchemy
from tests.test_utils import in_data_dir


class ShouldCreateAlchemyTestCase(unittest.TestCase):

    def setUp(self):
        self.catalogue = catalogue.CatalogueDatabase(memory=True, drop=True)
        self.session = self.catalogue.session

    def tearDown(self):
        self.session.commit()

    def test_drop(self):
        self.catalogue = catalogue.CatalogueDatabase(
            drop=True, filename=in_data_dir("test_drop.db"))
        self.catalogue = catalogue.CatalogueDatabase(memory=True, drop=True)

    def test_eventsource(self):
        event_source = catalogue.EventSource(name="test1")
        self.session.add(event_source)
        self.assertEqual(self.session.query(
            catalogue.EventSource).filter_by(name='test1').count(), 1)

    def test_agency(self):
        eventsource = catalogue.EventSource(name="test2")
        self.session.add(eventsource)

        agency = catalogue.Agency(source_key="test", eventsource=eventsource)
        self.session.add(agency)
        self.assertEqual(
            self.session.query(catalogue.Agency).filter_by(
                source_key='test').count(),
            1)

    def test_event(self):
        eventsource = catalogue.EventSource(name="test3")
        self.session.add(eventsource)

        event = catalogue.Event(source_key="test", eventsource=eventsource)
        self.session.add(event)
        self.assertEqual(
            self.session.query(catalogue.Event).filter_by(
                source_key='test').count(), 1)

    def test_origin(self):
        eventsource = catalogue.EventSource(name="test4")
        self.session.add(eventsource)

        origin = catalogue.Origin(source_key="test", eventsource=eventsource,
                                 position=geoalchemy.WKTSpatialElement(
                                     'POINT(-81.40 38.08)'),
                                 time=datetime.now(),
                                 depth=3)
        self.session.add(origin)
        self.assertEqual(
            self.session.query(catalogue.Origin).filter(
                catalogue.Origin.depth > 2).count(), 1)

    def test_magnitudemeasure(self):
        eventsource = catalogue.EventSource(name="test4")
        self.session.add(eventsource)

        event = catalogue.Event(source_key="test", eventsource=eventsource)
        self.session.add(event)

        agency = catalogue.Agency(source_key="test", eventsource=eventsource)
        self.session.add(agency)

        origin = catalogue.Origin(
            source_key="test", eventsource=eventsource,
            position=geoalchemy.WKTSpatialElement('POINT(-81.40 38.08)'),
            time=datetime.now(),
            depth=1)
        self.session.add(origin)

        measure = catalogue.MagnitudeMeasure(
            event=event, agency=agency, origin=origin, scale='mL', value=5.0)
        self.session.add(measure)

        self.assertEqual(
            self.session.query(catalogue.MagnitudeMeasure).count(), 1)

    def test_get_or_add(self):
        event_source1, created = self.catalogue.get_or_create(
            catalogue.EventSource, {'name': "test_5"})
        self.assertTrue(created)
        event_source2, created = self.catalogue.get_or_create(
            catalogue.EventSource, {'name': "test_5"})
        self.assertFalse(created)
        self.assertEqual(event_source1, event_source2)

    def create_test_fixture(self):
        eventsource = catalogue.EventSource(name="AnEventSource")
        self.session.add(eventsource)

        first_event = catalogue.Event(source_key="1st",
                    eventsource=eventsource)
        second_event = catalogue.Event(source_key="2nd",
                    eventsource=eventsource)
        self.session.add(first_event)
        self.session.add(second_event)

        agency_one = catalogue.Agency(source_key="1st",
                eventsource=eventsource, name='Tatooine')
        agency_two = catalogue.Agency(source_key="2nd",
                eventsource=eventsource, name='Alderaan')
        agency_three = catalogue.Agency(source_key="3rd",
                eventsource=eventsource, name='DeathStar')
        self.session.add(agency_one)
        self.session.add(agency_two)
        self.session.add(agency_three)

        origin = catalogue.Origin(
            source_key="test", eventsource=eventsource,
            position=geoalchemy.WKTSpatialElement('POINT(-81.40 38.08)'),
            time=datetime.now(),
            depth=1)
        self.session.add(origin)

        measure_one = catalogue.MagnitudeMeasure(
            event=first_event, agency=agency_one,
            origin=origin, scale='mL', value=5.0)
        self.session.add(measure_one)

        measure_two = catalogue.MagnitudeMeasure(
           event=second_event, agency=agency_two,
           origin=origin, scale='mb', value=6.0)
        self.session.add(measure_two)

    def test_available_measures_agencies(self):
        # Created 2 measures with related Agencies Tatooine and Alderaan
        # added another Agency with no linked measure DeathStar.
        self.create_test_fixture()

        self.assertEqual(set(['Tatooine', 'Alderaan']),
                    self.catalogue.get_available_measure_agencies())

    def test_available_measures_scales(self):
        self.create_test_fixture()

        self.assertEqual(set(['mL', 'mb']),
                    self.catalogue.get_available_measure_scales())

    def test_get_summary(self):
        self.create_test_fixture()

        self.assertEqual({catalogue.CatalogueDatabase.MEASURE_AGENCIES:
                            set(['Tatooine', 'Alderaan']),
                          catalogue.CatalogueDatabase.MEASURE_SCALES:
                            set(['mL', 'mb'])},
                            self.catalogue.get_summary())
