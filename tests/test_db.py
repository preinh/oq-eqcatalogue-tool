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
        self.catalogue = catalogue.CatalogueDatabase(memory=True, drop=True)
        self.catalogue = catalogue.CatalogueDatabase(
            drop=True, filename=in_data_dir("test_drop.db"))

    def create_test_fixture(self):
        event_source = "AnEventSource"

        agency_one = "Tatooine"
        agency_two = 'Alderaan'

        origin_one = dict(
            origin_key="test",
            position=geoalchemy.WKTSpatialElement('POINT(-81.40 38.08)'),
            time=datetime(1950, 2, 19, 23, 14, 5),
            depth=1)

        origin_two = dict(
            origin_key="test",
            position=geoalchemy.WKTSpatialElement('POINT(-81.40 38.08)'),
            time=datetime(1987, 2, 6, 9, 14, 15),
            depth=1)

        measure_one = catalogue.MagnitudeMeasure(
            event_source=event_source,
            event_key='1st',
            agency=agency_one, scale='mL', value=5.0,
            **origin_one)
        self.session.add(measure_one)

        measure_two = catalogue.MagnitudeMeasure(
            event_source=event_source,
            event_key='2nd',
            agency=agency_two,
            scale='mb', value=6.0, **origin_two)
        self.session.add(measure_two)

    def test_available_measures_agencies(self):
        self.create_test_fixture()

        self.assertEqual(set(['Tatooine', 'Alderaan']),
                         self.catalogue.get_agencies())

    def test_available_measures_scales(self):
        self.create_test_fixture()

        self.assertEqual(set(['mL', 'mb']),
                         self.catalogue.get_measure_scales())

    def test_get_dates(self):
        self.create_test_fixture()
        exp_min_date = datetime(1950, 2, 19, 23, 14, 5)
        exp_max_date = datetime(1987, 2, 6, 9, 14, 15)
        dates = self.catalogue.get_dates()

        self.assertEqual(exp_min_date, dates[0])
        self.assertEqual(exp_max_date, dates[1])

    def test_get_summary(self):
        self.create_test_fixture()

        self.assertEqual({
            catalogue.CatalogueDatabase.MEASURE_AGENCIES:
            set(['Tatooine', 'Alderaan']),
            catalogue.CatalogueDatabase.MEASURE_SCALES:
            set([u'mL', u'mb'])},
            self.catalogue.get_summary())
