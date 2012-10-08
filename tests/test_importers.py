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
from StringIO import StringIO


from eqcatalogue.importers import (
    CsvEqCatalogueReader, Converter, BaseImporter,
    Iaspei, V1, isf_bulletin as isf)

from eqcatalogue.importers.reader_utils import (STR_TRANSF, INT_TRANSF,
                                                FLOAT_TRANSF)
from eqcatalogue.exceptions import InvalidMagnitudeSeq, ParsingFailure

from eqcatalogue import models as catalogue

from tests.test_utils import in_data_dir


DATAFILE_ISC = in_data_dir('isc-query-small.html')
BROKEN_ISC = in_data_dir('broken_isc.txt')
UK_SCALE_ISC = in_data_dir('isc_with_uk_scale.txt')
DATAFILE_IASPEI = in_data_dir('iaspei.csv')


class ShouldImportFromISFBulletinV1(unittest.TestCase):

    def setUp(self):
        self.f = file(DATAFILE_ISC)
        self.broken_isc = file(BROKEN_ISC)
        self.uk_scale_isc = file(UK_SCALE_ISC)
        self.cat = catalogue.CatalogueDatabase(memory=True, drop=True)

    def tearDown(self):
        self.f.close()
        self.broken_isc.close()

    def test_detect_junk_lines(self):
        # Common Assess part in setUp method

        # Act
        importer = V1(self.f, self.cat)

        # Assert
        ret = importer.store(allow_junk=False)

        self.assertTrue(len(ret[BaseImporter.ERRORS]) > 0)

    def test_parse_html_file(self):
        # Common Assess part in setUp method

        # Act
        v1_importer = V1(self.f, self.cat)
        v1_importer.store()

        # Assert
        self.assertEqual(v1_importer.summary, {
                    BaseImporter.EVENT_SOURCE: 1,
                    BaseImporter.AGENCY: 17,
                    BaseImporter.EVENT: 18,
                    BaseImporter.ORIGIN: 128,
                    BaseImporter.MEASURE:  334,
                    })

        sources = self.cat.session.query(catalogue.EventSource)
        agencies = self.cat.session.query(catalogue.Agency)
        events = self.cat.session.query(catalogue.Event)
        origins = self.cat.session.query(catalogue.Origin)
        measures = self.cat.session.query(catalogue.MagnitudeMeasure)

        self.assertEqual(sources.count(),  1)
        self.assertEqual(agencies.count(),  17)
        self.assertEqual(events.count(),  18)
        self.assertEqual(origins.count(),  128)
        self.assertEqual(measures.count(),  334)

    def test_raises_parsing_failure(self):
        importer = V1(self.broken_isc, self.cat)
        BROKEN_LINE_NUM = 18
        with self.assertRaises(ParsingFailure) as exp:
            importer.store()

            self.assertEqual(isf.ERR_MSG % BROKEN_LINE_NUM, exp.message)

    def test_import_with_uk_scale(self):
        importer = V1(self.uk_scale_isc, self.cat)
        importer.store()
                # Assert
        self.assertEqual(importer.summary, {
                    BaseImporter.EVENT_SOURCE: 1,
                    BaseImporter.AGENCY: 5,
                    BaseImporter.EVENT: 1,
                    BaseImporter.ORIGIN: 5,
                    BaseImporter.MEASURE:  4,
                    BaseImporter.ERRORS: []
                    })


class AIaspeiImporterShould(unittest.TestCase):

    def setUp(self):
        self.file = file(DATAFILE_IASPEI)
        self.cat = catalogue.CatalogueDatabase(memory=True, drop=True)
        self.csv_importer = Iaspei(self.file, self.cat)

    def tearDown(self):
        self.file.close()

    def test_raise_exception_with_invalid_mag_group(self):
        # Each mag is well defined when there are Author, Type and Value
        mag_group = ['IASPEI', 'MS', '3.4', 'IASPEI', 'mb', '4.3', 'NEIC']
        with self.assertRaises(InvalidMagnitudeSeq) as exp:
            self.csv_importer._check_magnitude_group(mag_group)

            self.assertEqual(Iaspei.ERR_MAG_GROUP, exp.message)

    def test_csv_parsing(self):
        csv_file = StringIO(
            '10525612,IASPEI,2008-02-09,07:12:06.43,32.4850,-115.2935, 20.6,,'
            'IASPEI,MS,4.7,IASPEI,mb, 4.9\n'
            '10526626,IASPEI,2008-02-11,18:29:32.64,32.4765,-115.2965,16.5,,'
            'IASPEI,MS,4.8,IASPEI,mb, 4.8\n')
        importer = Iaspei(csv_file, self.cat)
        exp_num_entries = 2
        self.assertEqual(exp_num_entries, len(
            importer._parse_csv(header=False)))

    def test_import_csv_iaspei(self):
        self.csv_importer.store()
        summary = self.csv_importer.summary

        self.assertEqual(summary, {
            BaseImporter.EVENT_SOURCE: 1,
            BaseImporter.AGENCY: 1,
            BaseImporter.EVENT: 46,
            BaseImporter.ORIGIN: 46,
            BaseImporter.MEASURE:  61,
            BaseImporter.ERRORS: []
        })

        importer = Iaspei(self.file, self.cat)
        importer.store()

    def test_importing_once_the_same_csv(self):

        first_importer = Iaspei(self.file, self.cat)
        first_importer.store()

        second_importer = Iaspei(self.file, self.cat)
        second_importer.store()

        sources = self.cat.session.query(catalogue.EventSource)
        agencies = self.cat.session.query(catalogue.Agency)
        events = self.cat.session.query(catalogue.Event)
        origins = self.cat.session.query(catalogue.Origin)
        measures = self.cat.session.query(catalogue.MagnitudeMeasure)

        self.assertEqual(sources.count(),  1)
        self.assertEqual(agencies.count(),  1)
        self.assertEqual(events.count(),  46)
        self.assertEqual(origins.count(),  46)
        self.assertEqual(measures.count(),  61)


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
                                'originID': '4644028', 'phases': 6,
                                'solutionKey': '1', 'solutionDesc': '1_IDC_ML',
                                'timeError': 1.29, 'solutionID': '4644028',
                                'semiMajor90': 61.5, 'semiMinor90': 18.6,
                                'Longitude': 97.9598, 'errorAzimuth': 73.0,
                                'maxDistance': 59.32, 'day': 3, 'minute': 37,
                                'mag_type': 'ML', 'magStations': 1, 'hour': 21,
                                'stations': None, 'depth': 0.0,
                                'magnitude': 3.9, 'eventKey': '1009476',
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
