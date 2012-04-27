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

class ShouldCreateAlchemyTestCase(unittest.TestCase):

    def setUp(self):
        cat = catalogue.CatalogueDatabase()
        cat.setup(drop=True, memory=True)
        self.session = cat.session

    def test_eventsource(self):
        event_source = catalogue.EventSource(name="test1")
        self.session.add(event_source)
        self.assertEqual(self.session.query(catalogue.EventSource).filter_by(name='test1').count(), 1)

    def test_agency(self):
        eventsource = catalogue.EventSource(name="test2")
        self.session.add(eventsource)

        agency = catalogue.Agency(source_key="test", eventsource=eventsource)
        self.session.add(agency)
        self.assertEqual(self.session.query(catalogue.Agency).filter_by(source_key='test').count(), 1)

    def test_event(self):
        eventsource = catalogue.EventSource(name="test3")
        self.session.add(eventsource)

        event = catalogue.Event(source_key="test", eventsource=eventsource)
        self.session.add(event)
        self.assertEqual(self.session.query(catalogue.Event).filter_by(source_key='test').count(), 1)

    def test_origin(self):
        eventsource = catalogue.EventSource(name="test4")
        self.session.add(eventsource)

        origin = catalogue.Origin(source_key="test", eventsource=eventsource,
                                 position=geoalchemy.WKTSpatialElement('POINT(-81.40 38.08)'),
                                 time = datetime.now(),
                                 depth=3)
        self.session.add(origin)
        self.assertEqual(self.session.query(catalogue.Origin).filter(catalogue.Origin.depth > 2).count(), 1)

    def test_magnitudemeasure(self):
        eventsource = catalogue.EventSource(name="test4")
        self.session.add(eventsource)

        event = catalogue.Event(source_key="test", eventsource=eventsource)
        self.session.add(event)

        agency = catalogue.Agency(source_key="test", eventsource=eventsource)
        self.session.add(agency)

        origin = catalogue.Origin(source_key="test", eventsource=eventsource,
                                 position=geoalchemy.WKTSpatialElement('POINT(-81.40 38.08)'),
                                 time = datetime.now(),
                                 depth=1)
        self.session.add(origin)

        measure = catalogue.MagnitudeMeasure(event=event, agency=agency, origin=origin, scale='mL', value=5.0)
        self.session.add(measure)

        self.assertEqual(self.session.query(catalogue.MagnitudeMeasure).count(), 1)


    def tearDown(self):
        self.session.commit()
