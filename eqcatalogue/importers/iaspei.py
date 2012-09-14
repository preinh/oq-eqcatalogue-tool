# Copyright (c) 2010-2012, GEM Foundation.
#
# eqcataloguetool is free software: you can redistribute it and/or modify it
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
# along with eqcataloguetool. If not, see <http://www.gnu.org/licenses/>.

from csv import DictReader
from datetime import datetime

from eqcatalogue import models as catalogue

class IaspeiReader(object):

    EVENTID_INDEX = 0
    AUTHOR_INDEX = 1
    DATE_INDEX = 2
    TIME_INDEX = 3
    LAT_INDEX = 4
    LON_INDEX = 5
    DEPTH_INDEX = 6
    DEPFIX_INDEX = 7

    MAG_GROUP_INDEX = 8
    MAG_MEASURE_ITEMS = 3


    def __init__(self, stream, catalogue):
        """
        Initialize the importer.

        :param: stream:
          A stream object storing the seismic event data
        :type stream: file

        :param: cat:
          The catalogue database used to import the data
        :type catalogue: CatalogueDatabase
        """
        self._stream = stream
        self._catalogue = catalogue
        self._summary = {'eventsource_created': 0,
                         'agency_created': 0,
                         'event_created': 0,
                         'origin_created': 0,
                         'measure_created': 0}


    def _parse_csv(self, header):
        entries = []
        for line in self._stream:
            entries.append([item.strip() for item in line.split(',')])
        if header:
            #skip the header line
            entries = entries[1:]

        return entries

    def store(self, header=True):
        """
        Read and parse from the input stream the data and insert them
        into the catalogue db.
        """

        entries =  self._parse_csv(header)
        print len(entries)
        for entry in entries:

            event_source, created = self._catalogue.get_or_create(
                    catalogue.EventSource, {'name': 'IASPEI'})
            if created:
                self._increase_key_in_summary('eventsource_created')

            event, created = self._catalogue.get_or_create(catalogue.Event,
                {'source_key': entry[self.EVENTID_INDEX],
                 'eventsource': event_source})
            if created:
                self._increase_key_in_summary('event_created')


            if len(entry[self.MAG_GROUP_INDEX:]) % 3 != 0:
                raise RuntimeError('Each Magnitude should be defined by '
                                   '3 Values: Author, Type and Value')

            # Time String Creation
            microsec = int(float(entry[self.TIME_INDEX][8:]) * 10000)
            time = ''.join([entry[self.TIME_INDEX][:9], str(microsec)])
            date_time = '/'.join(
                [entry[self.DATE_INDEX], time])

            values={'time': datetime.strptime(
                            date_time, '%Y-%m-%d/%H:%M:%S.%f'),
                    'position': self._catalogue.position_from_latlng(
                        entry[self.LAT_INDEX], entry[self.LON_INDEX]),
                    'depth': float(entry[self.DEPTH_INDEX]),
                    'eventsource': event_source,
                    #todo can eat your kittens
                    'source_key': entry[self.EVENTID_INDEX]}

            magnitude_group = entry[self.MAG_GROUP_INDEX:]

            for mag_group_start in xrange(0, len(magnitude_group),
                self.MAG_MEASURE_ITEMS):

                agency, created = self._catalogue.get_or_create(catalogue.Agency,
                                {'source_key': magnitude_group[mag_group_start],
                                 'eventsource': event_source})
                if created:
                    self._increase_key_in_summary('agency_created')

                origin, created = self._catalogue.get_or_create(catalogue.Origin, values)
                if created:
                    self._increase_key_in_summary('origin_created')
                mag_measure,  created = self._catalogue.get_or_create(
                    catalogue.MagnitudeMeasure,
                    {'event': event,
                     'agency': agency,
                     'scale': magnitude_group[mag_group_start + 1],
                     'value': magnitude_group[mag_group_start + 2],
                     'origin': origin
                     })
                if created:
                    self._increase_key_in_summary('measure_created')

        self._catalogue.session.commit()

        return self._summary


    def _increase_key_in_summary(self, key):
        self._summary[key] += 1



