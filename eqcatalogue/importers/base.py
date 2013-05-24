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

import collections
from sqlalchemy import distinct, func
from eqcatalogue.models import MagnitudeMeasure
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
    ORIGIN = 'Origins_Created'
    MEASURE = 'Measures_Created'

    def __init__(self, file_stream, db_catalogue):
        self._file_stream = file_stream
        self._catalogue = db_catalogue

        s = self._catalogue.session
        s.execute("PRAGMA synchronous=OFF")
        s.execute("PRAGMA count_changes=OFF")
        s.execute("PRAGMA journal_mode=OFF")
        s.execute("PRAGMA temp_store=OFF")
        s.autocommit = False
        s.autoflush = False

        self._before = collections.Counter(
            {self.EVENT_SOURCE: self.counter('event_source'),
             self.AGENCY: self.counter('agency'),
             self.ORIGIN: self.counter('origin_key'),
             self.MEASURE: self.counter('id')})

        self.errors = []

    def counter(self, field):
        return self._catalogue.session.query(
            func.count(distinct(getattr(MagnitudeMeasure, field)))).scalar()

    @abc.abstractmethod
    def store(self, **kwargs):
        """
        Read the input stream data and insert them
        into the catalogue db, during the process,
        a summary of inserted items is updated.

        :returns: the summary of the inserted/updated catalogue data
        """

    @property
    def summary(self):
        """
        Returns a dictionary where each key and associated value
        represents the number of entities, stored in the catalogue db.
        """
        summary = collections.Counter(
            {self.EVENT_SOURCE: self.counter('event_source'),
             self.AGENCY: self.counter('agency'),
             self.ORIGIN: self.counter('origin_key'),
             self.MEASURE: self.counter('id')})

        return dict(summary - self._before)
