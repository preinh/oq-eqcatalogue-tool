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

from eqcatalogue.importers.base import BaseImporter


class Importer(BaseImporter):
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

    def store(self, header=True):
        """
        Read and parse from the input stream the data and insert them
        into the catalogue db, a summary of entities stored is returned.
        """

        event_source = 'IASPEI'

        for entry in self._parse_csv(header):
            self._check_magnitude_group(entry[self.MAG_GR_INDEX:])

            # Time String Creation
            microsec = int(float(entry[self.TIME_INDEX][8:]) * 10000)
            time = ''.join([entry[self.TIME_INDEX][:9], str(microsec)])
            date_time = '/'.join(
                [entry[self.DATE_INDEX], time])

            if entry[self.DEPTH_INDEX]:
                depth = float(entry[self.DEPTH_INDEX])
            else:
                depth = None

            origin = {'time': datetime.strptime(
                date_time, '%Y-%m-%d/%H:%M:%S.%f'),
                'position': self._catalogue.position_from_latlng(
                    entry[self.LAT_INDEX], entry[self.LON_INDEX]),
                'depth': depth,
                'origin_key': entry[self.EVENTID_INDEX]}

            magnitude_group = entry[self.MAG_GR_INDEX:]

            for mag_group_start in xrange(
                    0, len(magnitude_group), self.MAG_MEASURE_ITEMS):
                agency = magnitude_group[mag_group_start]

                params = {
                    'event_key': entry[self.EVENTID_INDEX],
                    'event_source': event_source,
                    'agency': agency,
                    'scale': magnitude_group[mag_group_start + 1],
                    'value': magnitude_group[mag_group_start + 2],
                }
                params.update(origin)
                self._catalogue.session.add(
                    catalogue.MagnitudeMeasure(**params))

        self._catalogue.session.commit()

        return self.summary
