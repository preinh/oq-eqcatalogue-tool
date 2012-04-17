# Copyright (c) 2010-2012, GEM Foundation.
#
# EqCatalogueTool is free software: you can redistribute it and/or modify it
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
# along with EqCatalogueTool. If not, see <http://www.gnu.org/licenses/>.

"""
Module :mod:`eq_catalogue_tool.reader` defines classes for reading
different formats of earthquake catalogues.
"""

from csv import DictReader

from EqCatalogue.catalogue import CSV_FIELDNAMES, TRANSF_MAP


class CsvEqCatalogueReader(object):
    """
    EqCatalogueReader reads earthquake
    events descriptions, defined in a csv file.

    :param fileobj: csv file object
    :type fileobj: file object
    """

    def __init__(self, fileobj):
        self.fileobj = fileobj

    def read(self, converter):
        """
        Read method generates csv entries, after applying
        defined transformations.
        """
        reader = DictReader(self.fileobj, fieldnames=CSV_FIELDNAMES)
        for entry in reader:
            converted_entry = converter.convert(entry)
            yield converted_entry


class Converter(object):
    """
    Converter convertes all fields defined in the entry
    to the appropriate types, if a conversion for a field
    is not possible its value is updated to None.

    :param conversion_map: defines for every key the list of transformations
            that are going to be applied.
    :type conversion_map: dict
    """

    def __init__(self, conversion_map=None):
        if not conversion_map:
            self.conv_map = TRANSF_MAP
        else:
            self.conv_map = conversion_map

    def convert(self, entry):
        """
        Convert all values defined in the entry applying
        a list of transformations.

        :param entry: csv entry to be converted
        :type entry: dict
        :returns: csv entry converted
        :rtype: dict
        """

        for key, value in entry.iteritems():
            try:
                entry[key] = self._apply_transformations(key, value)
            except ValueError:
                entry[key] = None

        return entry

    def _apply_transformations(self, key, value):
        """
        Apply in sequence the transformations defined
        in the conversion map `self.conv_map` to the value.
        """

        transformations = self.conv_map[key]
        for transf in transformations:
            value = transf(value)

        return value
