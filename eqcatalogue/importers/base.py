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

"""
Module :mod:`eqcatalogue.importers.base` defines base classes for different
kinds of :class:` earthquake catalogue readers <CatalogueReader>`.
"""

import abc


def store_events(cls, stream, cat, **kwargs):
    """
     Utility that create an instance of the importer and load the
     data from `stream`
    """
    importer = cls(stream, cat)
    return importer.store(**kwargs)


class BaseImporter(object):
    """
    Base class for Importers.
    """

    __metaclass__ = abc.ABCMeta

    EVENT_SOURCE = 'EventSources_Created'
    AGENCY = 'Agencies_Created'
    EVENT = 'Events_Created'
    ORIGIN = 'Origins_Created'
    MEASURE = 'Measures_Created'
    ERRORS = 'Errors'

    def __init__(self, file_stream, db_catalogue):
        self._file_stream = file_stream
        self._catalogue = db_catalogue
        self._summary = {self.EVENT_SOURCE: 0,
                         self.AGENCY: 0,
                         self.EVENT: 0,
                         self.ORIGIN: 0,
                         self.MEASURE: 0,
                         self.ERRORS: []}

    @abc.abstractmethod
    def store(self, **kwargs):
        """
        Read the input stream data and insert them
        into the catalogue db, during the process,
        a summary of inserted items is updated.

        :returns: the summary of the inserted/updated catalogue data
        """

    @abc.abstractmethod
    def update_summary(self):
        """
        Update the summary key values.
        """

    @property
    def summary(self):
        """
        Returns a dictionary where each key and associated value
        represents the number of entities, stored in the catalogue db.
        """

        return self._summary
