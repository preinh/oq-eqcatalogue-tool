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
This module contains the class definitions of the basic domain models.
"""


DEFAULT_ENGINE = 'eqcatalogue.datastores.spatialite'

SCALES = ('mL', 'mb', 'Mb',
          'Ms', 'md', 'MD',
          'MS', 'mb1', 'mb1mx',
          'ms1', 'ms1mx', 'ML',
          'Ms1', 'mbtmp', 'Ms7',
          'mB', 'Md', 'Ml', 'M',
          'MG', 'ml', 'mpv',
          'mbLg', 'MW', 'Mw',
          'MLv', 'mbh', 'MN',
          'ME',
          'Muk'  # unknown magnitude (JMA)
    )

METADATA_TYPES = ('phases', 'stations',
                  'azimuth_gap', 'azimuth_error',
                  'min_distance', 'max_distance',
                  'num_stations')


class EventSource(object):
    """A source of event catalogues. E.g. ISC Web Catalogue

    We assume that for each event source there is only one file format
we import data from

    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db

    :py:attribute:: name
    an unique event source short name.
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "EventSource %s" % self.name


class Agency(object):
    """The agency which recorded and measured the events.

    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db

    :py:attribute:: source_key
    the identifier used by the event source for the object

    :py:attribute:: eventsource
    the source object we have imported the agency from. It is unique
    together with `source_key`
"""
    def __repr__(self):
        return "Agency %s" % self.source_key

    def __init__(self, source_key, eventsource):
        self.source_key = source_key
        self.eventsource = eventsource


class Event(object):
    """Describes a sismic event.

    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db

    :py:attribute:: source_key
    the identifier used by the event source for the object

    :py:attribute:: name
    an event name

    :py:attribute:: eventsource
    the source object we have imported the agency from. unique
    together with `source_key`
"""

    def __init__(self, source_key, eventsource, name=None):
        self.source_key = source_key
        self.eventsource = eventsource
        if name:
            self.name = name

    def __repr__(self):
        return "Event %s from %s" % (self.source_key,
                                     self.eventsource)


class MagnitudeMeasure(object):
    """Describes a single measure of the magnitude of an event
    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db

    :py:attribute:: event
    the event object associated with this measure

    :py:attribute:: agency
    the agency that has provided the measure

    :py:attribute:: origin
    the origin related to this measure

    :py:attribute:: scale
    the scale used for this measure.
    It is unique together with `agency_id` and `origin_id`

    :py:attribute:: value
    the magnitude expressed in the unit suitable for the scale used

    :py:attribute:: standard_error
    the standard magnitude error
    """

    def __init__(self, agency, event, origin, scale, value,
                 standard_error=None):
        assert(scale in SCALES)
        self.agency = agency
        self.event = event
        self.origin = origin
        self.scale = scale
        self.value = value
        if standard_error:
            self.standard_error = standard_error

    def __repr__(self):
        return "measure of %s at %s by %s: %s %s (sigma=%s)" % (
            self.event, self.origin, self.agency, self.value, self.scale,
            self.standard_error)


class Origin(object):
    """
    Describes a point at a given depth and a time.
    For each quantity a measure of the  accuracy is described.

    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db

    :py:attribute:: source_key
    the identifier used by the event source for the object

    :py:attribute:: time
    Time in format "YYYY-MM-DD HH:MM:SS.SSS".

    :py:attribute:: time_error
    Time errors expressed in seconds.

    :py:attribute:: time_rms
    Time error expressed as a Root Mean Square in seconds.

    :py:attribute:: position
    Point coordinate (latitude and longitude)

    :py:attribute:: semi_major_90error
    Semi-Major axis of the 90th percentile confidence ellipsis of the
    epicentre.

    :py:attribute:: semi_minor_90error
    Semi-Minor axis of the 90th percentile confidence ellipsis of the
    epicentre.

    :py:attribute:: azimuth_error
    Azimuth with respect to geographical north of the Semi-Major axis.

    :py:attribute:: depth
    depth of the hypocentre in km.

    :py:attribute:: depth_error
    Error in km on the hypocentre depth.

    :py:attribute:: eventsource
    the source object we have imported the origin from. unique
    together with `source_key`
"""
    def __repr__(self):
        return "Origin %s %s" % (self.id, self.source_key)

    def __init__(self, position, time, eventsource, source_key,
                 **kwargs):
        self.time = time
        self.position = position
        self.eventsource = eventsource
        self.source_key = source_key
        for k, v in kwargs.items():
            setattr(self, k, v)


class MeasureMetadata(object):
    """Metadata of a measurement.
    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db

    :py:attribute:: magnitudemeasure
    the measure, the metadata is associated with

    :py:attribute:: name
    the name of the metadata. It is unique together with magnitudemeasure

    :py:attribute:: value
    the float value of the metadata.
    """
    def __repr__(self):
        return "%s = %s" % (self.name, self.value)

    def __init__(self, metadata_type, value, magnitudemeasure):
        assert(metadata_type in METADATA_TYPES)
        self.name = metadata_type
        self.value = value
        self.magnitudemeasure = magnitudemeasure


class Singleton(type):
    """Metaclass to implement the singleton pattern"""
    def __init__(cls, name, bases, d):
        super(Singleton, cls).__init__(name, bases, d)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class CatalogueDatabase(object):
    """
    This is the main class used to access the database. It is a
    singleton object, so it is instantiated only once in your
    application
    """

    __metaclass__ = Singleton

    def __init__(self, engine_class_module=DEFAULT_ENGINE, **engine_params):
        self._engine_class = self.__class__.get_engine(engine_class_module)
        self._engine = self._engine_class(**engine_params)

    def recreate(self):
        self._engine.recreate()

    @classmethod
    def reset_singleton(cls):
        cls.instance = None

    @classmethod
    def get_engine(cls, module_name):
        module = __import__(module_name, fromlist=['Engine'])
        return module.Engine

    def position_from_latlng(self, latitude, longitude):
        return self._engine_class.position_from_latlng(latitude, longitude)

    @property
    def session(self):
        return self._engine.session

    def get_or_create(self, class_object, query_args, creation_args=None):
        """Handy method to create an object of type `class_object`
        given the query conditions in `query_args`. If an object
        already exists it returns it, otherwise it creates the object
        with params given by `creation_args`"""
        query = self.session.query(class_object)
        queryset = query.filter_by(**query_args)
        if queryset.count():
            return queryset[0], False
        else:
            if not creation_args:
                creation_args = query_args
            else:
                creation_args.update(query_args)
            obj = class_object(**creation_args)
            self.session.add(obj)
            return obj, True
