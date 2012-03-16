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

from csv import DictReader

from catalogue import CSV_FIELDNAMES, TRANSF_MAP

class EqCatalogueReader(object):

    def __init__(self, fileobj):
        self.fileobj = fileobj

    def read(self, convert):
        reader = DictReader(self.fileobj, fieldnames=CSV_FIELDNAMES)
        for entry in reader:
            converted_entry = convert.do(entry)
            yield converted_entry


class Convert(object):

    def __init__(self, conversion_map=TRANSF_MAP):
        self.conv_map = conversion_map

    def do(self, entry):
        for key, value in entry.iteritems():
            try:
                transformations = TRANSF_MAP[key]
                for transf in transformations:
                    value = transf(value)
                entry[key] = value
            except ValueError:
                entry[key] = None

        return entry
