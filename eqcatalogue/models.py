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
GeoAlchemy model definition
"""

from datetime import datetime

from pysqlite2 import dbapi2 as sqlite

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.events import event as sqlevent

import geoalchemy

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

## We used non-declarative model mapping, as we need to define model
## at runtime (not at module import time). Actually, only at runtime
## we can load the spatialite extension and then the spatialite
## metadata needed by geoalchemy to build the orm (see
## CatalogueDatabase._setup)


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
        return "Event Source: %s" % self.name


class Agency(object):
    """The agency which recorded and measured the events.

    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db

    :py:attribute:: source_key
    the identifier used by the event source for the object

    :py:attribute:: name
    agency long name, short name (e.g. ISC, IDC, DMN) should be saved
    into source_key

    :py:attribute:: eventsource
    the source object we have imported the agency from. It is unique
    together with `source_key`
"""
    def __repr__(self):
        if self.name:
            return "Agency %s (%s)" % (self.name, self.name)
        else:
            return "Agency %s" % self.source_key

    def __init__(self, source_key, eventsource, name=None):
        self.source_key = source_key
        self.eventsource = eventsource
        if name:
            self.name = name


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
        return "Event %s (by %s)" % (self.source_key,
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
        return "measure of %s at %s by %s: %s %s" % (
            self.event, self.origin, self.agency, self.scale, self.value)


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
        return "%s@%s at %s" % (self.position, self.time, self.depth)

    def __init__(self, position, time, eventsource, source_key,
                 **kwargs):
        self.time = time
        self.position = position
        self.eventsource = eventsource
        self.source_key = source_key
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def position_from_latlng(latitude, longitude):
        position = geoalchemy.WKTSpatialElement(
            'POINT(%s %s)' % (latitude, longitude))
        return position


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
    def __init__(cls, name, bases, d):
        super(Singleton, cls).__init__(name, bases, d)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class CatalogueDatabase(object):
    """
    This is the main class used to access the database.
    """

    __metaclass__ = Singleton
    DEFAULT_FILENAME = "eqcatalogue.db"

    _instance = None

    def __init__(self, filename=None, memory=False, drop=False):
        self._engine = None
        self.session = None
        self._metadata = None
        self._setup(filename=filename, memory=memory, drop=drop)

    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""

        if not cls._instance:
            cls._instance = super(CatalogueDatabase, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def _setup(self, memory=False, filename=None, drop=False):
        """Setup a sqlalchemy connection to spatialite with the proper
        metadata.

        :param memory: if True the catalogue will use an in-memory
        database, otherwise a file-based database is used

        :param filename: the filename of the database used. Unused if
        `memory` is True

        :param drop: if True, drop the catalogue and rebuild the
        schema
        """

        if memory:
            self._engine = sqlalchemy.create_engine('sqlite://', module=sqlite)
        else:
            filename = filename or self.DEFAULT_FILENAME
            self._engine = sqlalchemy.create_engine(
                'sqlite:///%s' % filename,
                module=sqlite,
                poolclass=sqlalchemy.pool.QueuePool,
                pool_size=1,
                )
        sqlevent.listen(self._engine,
                        "first_connect",
                        _connect)
        self.session = orm.sessionmaker(bind=self._engine)()
        self._metadata = sqlalchemy.MetaData(self._engine)
        self._create_schema()
        if drop:
            self._metadata.drop_all()
        self._metadata.create_all(self._engine)

    def _create_schema_eventsource(self):
        """Create Event Source Schema"""
        metadata = self._metadata

        eventsource = sqlalchemy.Table(
            'catalogue_eventsource', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer,
                              primary_key=True),
            sqlalchemy.Column('created_at',
                              sqlalchemy.DateTime,
                              default=datetime.now()),
            sqlalchemy.Column('name',
                              sqlalchemy.String(255), unique=True))
        orm.Mapper(EventSource, eventsource)
        geoalchemy.GeometryDDL(eventsource)

    def _create_schema_agency(self):
        """Create the schema for the Agency model"""

        metadata = self._metadata

        agency = sqlalchemy.Table(
            'catalogue_agency', metadata,
            sqlalchemy.Column('id',
                              sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at',
                              sqlalchemy.DateTime, default=datetime.now()),
            sqlalchemy.Column('source_key',
                              sqlalchemy.String(), nullable=False),
            sqlalchemy.Column('eventsource_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey(
                    'catalogue_eventsource.id')),
            sqlalchemy.Column('name', sqlalchemy.String(255), unique=True))
        orm.Mapper(Agency, agency, properties={
                'eventsource': orm.relationship(
                    EventSource,
                    backref=orm.backref('agencies'))
                })
        geoalchemy.GeometryDDL(agency)

    def _create_schema_event(self):
        """Create the schema for the Event model"""

        metadata = self._metadata

        event = sqlalchemy.Table(
            'catalogue_event', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at',
                              sqlalchemy.DateTime, default=datetime.now()),
            sqlalchemy.Column('source_key',
                              sqlalchemy.String(), nullable=False),
            sqlalchemy.Column('name',
                              sqlalchemy.String(), nullable=True),
            sqlalchemy.Column('eventsource_id', sqlalchemy.Integer,
                              sqlalchemy.ForeignKey(
                    'catalogue_eventsource.id')))
        orm.Mapper(Event, event, properties={
                'eventsource': orm.relationship(EventSource,
                                                backref=orm.backref('events'))
                })
        geoalchemy.GeometryDDL(event)

    def _create_schema_magnitudemeasure(self):
        """Create the schema for the magnitude measure model"""

        metadata = self._metadata

        magnitudemeasure = sqlalchemy.Table(
            'catalogue_magnitudemeasure', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at',
                              sqlalchemy.DateTime, default=datetime.now()),
            sqlalchemy.Column('event_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey('catalogue_event.id')),
            sqlalchemy.Column('agency_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey('catalogue_agency.id')),
            sqlalchemy.Column('origin_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey('catalogue_origin.id')),
            sqlalchemy.Column('scale', sqlalchemy.Enum(*SCALES)),
            sqlalchemy.Column('value', sqlalchemy.Float()),
            sqlalchemy.Column('standard_error',
                              sqlalchemy.Float(), nullable=True))

        orm.Mapper(MagnitudeMeasure, magnitudemeasure, properties={
                'event': orm.relationship(Event,
                                          backref=orm.backref('measures')),
                'agency': orm.relationship(Agency,
                                           backref=orm.backref('measures')),
                'origin': orm.relationship(Origin,
                                           backref=orm.backref('measures'))
                })
        geoalchemy.GeometryDDL(magnitudemeasure)

    def _create_schema_origin(self):
        """Create the schema for the Origin model"""
        metadata = self._metadata
        origin = sqlalchemy.Table(
            'catalogue_origin', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at',
                              sqlalchemy.DateTime, default=datetime.now()),
            sqlalchemy.Column('source_key',
                              sqlalchemy.String(), nullable=False),
            sqlalchemy.Column('eventsource_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey(
                    'catalogue_eventsource.id')),
            sqlalchemy.Column('time', sqlalchemy.DateTime, nullable=False),
            sqlalchemy.Column('time_error', sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('time_rms', sqlalchemy.Float(), nullable=True),
            geoalchemy.GeometryExtensionColumn('position',
                                               geoalchemy.Point(2, srid=4326),
                                               nullable=False),
            sqlalchemy.Column('semi_minor_90error',
                              sqlalchemy.Float(),
                              nullable=True),
            sqlalchemy.Column('semi_major_90error',
                              sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('depth', sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('depth_error',
                              sqlalchemy.Float(), nullable=True))
        orm.Mapper(Origin, origin, properties={
                'eventsource': orm.relationship(
                    EventSource,
                    backref=orm.backref('origins')),
                'position': geoalchemy.GeometryColumn(origin.c.position)})
        geoalchemy.GeometryDDL(origin)

    def _create_schema_measuremetadata(self):
        """Create the schema for the measure metadata model"""

        metadata = self._metadata

        measuremetadata = sqlalchemy.Table(
            'catalogue_measuremetadata', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at', sqlalchemy.DateTime,
                              default=datetime.now()),
            sqlalchemy.Column('magnitudemeasure_id', sqlalchemy.Integer,
                              sqlalchemy.ForeignKey(
                    'catalogue_magnitudemeasure.id')),
            sqlalchemy.Column('name',
                              sqlalchemy.Enum(*METADATA_TYPES),
                              nullable=False),
            sqlalchemy.Column('value', sqlalchemy.Float(), nullable=False))
        orm.Mapper(MeasureMetadata, measuremetadata, properties={
                'magnitudemeasure': orm.relationship(
                    MagnitudeMeasure,
                    backref=orm.backref('metadata'))})
        geoalchemy.GeometryDDL(measuremetadata)

    def _create_schema(self):
        """Create and contains the model definition"""

        orm.clear_mappers()

        self._create_schema_eventsource()
        self._create_schema_agency()
        self._create_schema_event()
        self._create_schema_magnitudemeasure()
        self._create_schema_origin()
        self._create_schema_measuremetadata()

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


def _initialize_spatialite_db(connection):
    """Initialize Spatialite Database. Needed only when a newly
    freshed database or a corrupted one have to be used"""

    connection.execute('SELECT InitSpatialMetaData()')
    try:
        connection.execute("INSERT INTO spatial_ref_sys"
                           "(srid, auth_name, auth_srid,"
                           " ref_sys_name,proj4text)"
                           "VALUES (4326, 'epsg', 4326, 'WGS 84',"
                           " '+proj=longlat "
                           "+ellps=WGS84 +datum=WGS84 +no_defs')")
    except sqlite.IntegrityError:
        pass


def _load_extension(session):
    """Load spatial lite extension in `session`

    :param:: session:
    A sqlalchemy session."""

    try:
        session.execute("select load_extension('libspatialite.so')")
    except sqlite.OperationalError:
        try:
            session.execute("select load_extension('libspatialite.dylib')")
        except sqlite.OperationalError:
            try:
                session.execute(
                    "select load_extension('libspatialite.dll')")
            except:
                raise RuntimeError("""
Could not load libspatial extension.
Check your spatialite and pysqlite2 installation"""
                                   )
    try:
        session.execute('select * from spatial_ref_sys')
    except sqlite.OperationalError:
        _initialize_spatialite_db(session)


def _connect(dbapi_connection, connection_rec=None):
    """Enable load extension on connect. Event handler triggered
    by sqlalchemy"""
    dbapi_connection.enable_load_extension(True)
    _load_extension(dbapi_connection)
    if connection_rec:
        pass
