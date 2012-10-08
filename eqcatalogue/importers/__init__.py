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

"""
This package implements the importer (parser and db serializer) for
the following formats:

ISF Bulletin
IASPEI
"""

from __future__ import absolute_import

from .base import BaseImporter, store_events

from .iaspei import Importer as Iaspei
from .isf_bulletin import Importer as V1
from .csv1 import CsvEqCatalogueReader, Converter

__all__ = [x.__name__ for x in (BaseImporter, store_events, Iaspei,
                                V1, CsvEqCatalogueReader, Converter)]
