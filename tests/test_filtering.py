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
import random
from datetime import datetime
from geoalchemy import WKTSpatialElement

from tests.test_utils import in_data_dir

from eqcatalogue.importers.csv1 import CsvEqCatalogueReader, Converter
from eqcatalogue import models
from eqcatalogue import exceptions
from eqcatalogue import filtering


def load_fixtures(session):
    # Allows to insert test entries in the earthquake db.
    csv_filename = in_data_dir('query_catalogue.csv')
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


class ACriteriaShould(unittest.TestCase):

    def setUp(self):
        self.cat_db = models.CatalogueDatabase(memory=True, drop=True)
        self.cat_db.recreate()
        self.session = self.cat_db.session
        load_fixtures(self.session)

    def test_allows_filtering_of_all_measures(self):
        self.assertEqual(30, len(filtering.Criteria()))
        self.assertEqual(30, len(filtering.Criteria().all()))

    def test_behave_as_a_container(self):
        measure = random.choice(filtering.Criteria())
        self.assertTrue(measure in filtering.Criteria())

    def test_return_events(self):
        self.assertEqual(5, len(filtering.Criteria().events()))

    def test_group_measures(self):
        # we only test the presence of the interface as the proper
        # behavior of this feature is tested in other test modules
        self.assertTrue(filtering.Criteria().group_measures())

    def test_allows_filtering_measures_on_time_criteria(self):
        time = datetime.now()
        before_time = filtering.Before(time)
        after_time = filtering.After(time)
        time_lb = datetime(2001, 3, 2, 4, 11)
        time_ub = datetime(2001, 5, 2, 22, 34)
        between_time = filtering.Between((time_lb, time_ub))

        self.assertEqual(30, before_time.count())

        measure = random.choice(before_time)
        self.assertTrue(before_time.predicate(measure))

        self.assertEqual(0, after_time.count())

        self.assertEqual(6, between_time.count())
        measure = random.choice(between_time)
        self.assertTrue(between_time.predicate(measure))

    def test_allows_filtering_of_measures_given_two_mag(self):
        result = filtering.WithMagnitudeScales(('MS', 'mb'))
        self.assertEqual(20, len(result))

        measure = random.choice(result)
        self.assertTrue(result.predicate(measure))

        self.assertEqual(0, filtering.WithMagnitudeScales(
            'wtf').count())

    def test_allows_filtering_of_measures_given_a_mag(self):
        result = filtering.WithMagnitudeScale('MS')
        self.assertEqual(4, len(result))

        measure = random.choice(result)
        self.assertTrue(result.predicate(measure))

        self.assertEqual(0, filtering.WithMagnitudeScale(
            'wtf').count())

    def test_allows_filtering_of_measures_on_agency_basis(self):
        agency = 'LDG'
        self.assertEqual(2, len(filtering.WithAgencies([agency])))

        agency = 'NEIC'
        self.assertEqual(4, len(filtering.WithAgencies([agency])))

        agency = 'Blabla'
        self.assertEqual(0, len(filtering.WithAgencies([agency])))

        agencies = ['LDG', 'NEIC']
        self.assertEqual(6, len(filtering.WithAgencies(agencies)))

    def test_allows_filtering_of_measures_given_polygon(self):
        fst_polygon = 'POLYGON((85 35, 92 35, 92 25, 85 25, 85 35))'
        snd_polygon = 'POLYGON((92 15, 95 15, 95 10, 92 10, 92 15))'
        # Events inside first polygon: 1008566, 1008569, 1008570
        # with a sum for measures equal to 16.
        self.assertEqual(16, len(filtering.WithinPolygon(fst_polygon)))
        # Events inside second polygon: 1008567
        # with a sum for measures of 13.
        self.assertEqual(13, len(filtering.WithinPolygon(snd_polygon)))

    def test_indexing(self):
        measures = filtering.C()
        for i in range(0, len(measures)):
            self.assertTrue(measures[i] is not None)
        self.assertRaises(IndexError, measures.__getitem__, len(measures))

    def test_allows_filtering_of_measures_given_distance_from_point(self):
        distance = 700000  # distance is expressed in meters using srid 4326
        point = 'POINT(88.20 33.10)'
        self.assertEqual(16, len(filtering.WithinDistanceFromPoint(
            (point, distance))))

        distance = 250000
        self.assertEqual(3, len(filtering.WithinDistanceFromPoint(
            (point, distance))))

        distance = 228000
        self.assertEqual(0, len(filtering.WithinDistanceFromPoint(
            (point, distance))))

        distance = 2400000
        self.assertEqual(30, len(filtering.WithinDistanceFromPoint(
            (point, distance))))

    def test_allows_or_combination(self):
        agencies = ['LDG', 'NEIC']
        measures1 = filtering.WithAgencies(agencies)
        self.assertEqual(6, len(measures1))

        agencies = ['BJI']
        measures2 = filtering.WithAgencies(agencies)

        self.assertEqual(5, len(measures2))

        self.assertEqual(11, len(measures1 | measures2))

        measure = random.choice(random.choice([measures1, measures2]))
        self.assertTrue((measures1 | measures2).predicate(measure))

    def test_allows_and_combination(self):
        agencies = ['BJI']
        measures1 = filtering.WithAgencies(agencies)
        value = 5
        measures2 = filtering.WithMagnitudeGreater(value)

        result = measures1 & measures2
        self.assertEqual(2, len(result))
        for m in result:
            self.assertEqual('BJI', m.agency.source_key)
            self.assertTrue(m.value > value)

        measure = random.choice(result)
        self.assertTrue(result.predicate(measure))

    def test_default_predicate(self):
        measure = random.choice(filtering.C())
        self.assertTrue(filtering.C().predicate(measure))

    def test_factory(self):
        for criteria_arg, criteria_class in filtering.CRITERIA_MAP.items():
            arguments = {criteria_arg: ['fake', 'arguments']}
            criteria = filtering.C(**arguments)
            self.assertEqual(criteria_class, type(criteria))

        self.assertEqual(filtering.Criteria, type(filtering.C()))

        self.assertEqual(filtering.CombinedCriteria, type(filtering.C(
            agency__in=['ISC', 'NEIC'], magnitude__gt=5)))

        self.assertRaises(exceptions.InvalidCriteria, filtering.C,
                          kwargs={'wtf': 3})

    def tearDown(self):
        self.session.commit()


class TestCriteriaFactory(unittest.TestCase):
    """
    Test the Criteria factory
    """
    def setUp(self):
        self.TESTS = [
            ['before', filtering.Before, datetime.now()],
            ['after', filtering.After, datetime.now()],
            ['between', filtering.Between, [datetime.now(), datetime.now()]],
            ['agency__in', filtering.WithAgencies, ["LEIC"]],
            ['scale__in', filtering.WithMagnitudeScales, ["Mw"]],
            ['scale', filtering.WithMagnitudeScale, "Mw"],
            ['within_polygon', filtering.WithinPolygon,
             'POLYGON((92 15, 95 15, 95 10, 92 10, 92 15))'],
            ['within_distance_from_point', filtering.WithinDistanceFromPoint,
             ['POINT(88.20 33.10)', 10.]],
            ['magnitude__gt', filtering.WithMagnitudeGreater, 5.]]

    def test_types(self):
        """
        Test that the criteria factory build the objects of the proper
        types
        """
        for kwarg, criteria_class, value in self.TESTS:
            criteria = filtering.C(**{kwarg: value})
            self.assertEqual(criteria_class, criteria.__class__)
