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


import os

from eqcatalogue.importers import store_events, V1
from eqcatalogue.models import CatalogueDatabase

DATA_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../tests/data'))


def in_data_dir(filename):
    return os.path.join(DATA_DIR, filename)


def load_catalog():
    cat = CatalogueDatabase(memory=True)
    cat.recreate()
    store_events(V1, file(in_data_dir('isc-query-small.html')), cat)
    return cat
