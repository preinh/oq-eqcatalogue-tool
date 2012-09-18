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

from datetime import datetime

from eqcatalogue import models as catalogue
from eqcatalogue.exceptions import InvalidMagnitudeSeq

from eqcatalogue.importers.base import Importer


class Iaspei(Importer):
    """
    Implements the Importer for the Iaspei format.
    """

    (EVENTID_INDEX, AUTHOR_INDEX, DATE_INDEX, TIME_INDEX, LAT_INDEX,
     LON_INDEX, DEPTH_INDEX, DEPFIX_INDEX, MAG_GR_INDEX) = range(0, 9)

    MAG_MEASURE_ITEMS = 3

    ERR_MAG_GROUP = ('Each Magnitude should be defined by '
                     '3 Values: Author, Type and Value')

    def _parse_csv(self, header):
        """
        Returns a list of entries parsed in the csv file
        if the header is present in the csv it is skipped
        in the result.
        :param header:
            A flag which states if the header is in the csv file.
        """

        entries = []
        for line in self._file_stream:
            entries.append([item.strip() for item in line.split(',')])
        if header:
            #skip the header line
            entries = entries[1:]

        return entries

    def _check_magnitude_group(self, mag_group):
        """
        Check that for each magnitude in the sequence
        Author, Type and Value have been defined.
        """
        if len(mag_group) % 3 != 0:
            raise InvalidMagnitudeSeq(self.ERR_MAG_GROUP)

    def update_summary(self, item_key):
        self._summary[item_key] += 1

    def store(self, header=True):
        """
        Read and parse from the input stream the data and insert them
        into the catalogue db, a summary of entities stored is returned.
        """

        entries = self._parse_csv(header)
        for entry in entries:

            event_source, created = self._catalogue.get_or_create(
                    catalogue.EventSource, {'name': 'IASPEI'})
            if created:
                self.update_summary(Importer.EVENT_SOURCE)

            event, created = self._catalogue.get_or_create(catalogue.Event,
                {'source_key': entry[self.EVENTID_INDEX],
                 'eventsource': event_source})
            if created:
                self.update_summary(Importer.EVENT)

            self._check_magnitude_group(entry[self.MAG_GR_INDEX:])

            # Time String Creation
            microsec = int(float(entry[self.TIME_INDEX][8:]) * 10000)
            time = ''.join([entry[self.TIME_INDEX][:9], str(microsec)])
            date_time = '/'.join(
                [entry[self.DATE_INDEX], time])

            values = {'time': datetime.strptime(
                            date_time, '%Y-%m-%d/%H:%M:%S.%f'),
                        'position': self._catalogue.position_from_latlng(
                            entry[self.LAT_INDEX], entry[self.LON_INDEX]),
                        'depth': float(entry[self.DEPTH_INDEX]),
                        'eventsource': event_source,
                        'source_key': entry[self.EVENTID_INDEX]}

            magnitude_group = entry[self.MAG_GR_INDEX:]

            for mag_group_start in xrange(0, len(magnitude_group),
                self.MAG_MEASURE_ITEMS):

                agency, created = self._catalogue.get_or_create(
                    catalogue.Agency,
                    {'source_key': magnitude_group[mag_group_start],
                     'eventsource': event_source})
                if created:
                    self.update_summary(Importer.AGENCY)

                origin, created = self._catalogue.get_or_create(
                    catalogue.Origin, values)
                if created:
                    self.update_summary(Importer.ORIGIN)
                _,  created = self._catalogue.get_or_create(
                    catalogue.MagnitudeMeasure,
                    {'event': event,
                     'agency': agency,
                     'scale': magnitude_group[mag_group_start + 1],
                     'value': magnitude_group[mag_group_start + 2],
                     'origin': origin
                     })
                if created:
                    self.update_summary(Importer.MEASURE)


        self._catalogue.session.commit()
