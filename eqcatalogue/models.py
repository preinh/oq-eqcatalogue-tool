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
          'ms1', 'ms1mx')
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
    agency long name, short_name (e.g. ISC, IDC, DMN) should be saved
    into source_key

    :py:attribute:: eventsource
    the source object we have imported the agency from. It is unique
    together with `short_name`
"""
    def __repr__(self):
        if self.name:
            return "Agency %s (%s)" % (self.name, self.short_name)
        else:
            return "Agency %s" % self.short_name

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
                                     self.source)


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

    :py:attribute:: error
    the magnitude error
    (FIXME: please tell me if it is relative or absolute)

    """

    def __init__(self, agency, event, origin, scale, value):
        self.agency = agency
        self.event = event
        self.origin = origin
        self.scale = scale
        self.value = value

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

    def __init__(self, time, position, depth, eventsource, source_key):
        self.time = time
        self.position = position
        self.depth = depth
        self.eventsource = eventsource
        self.source_key = source_key


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


class CatalogueDatabase(object):
    """
    This is the main class used to access the database
    """

    DEFAULT_FILENAME = "eqcatalogue.db"

    def __init__(self, filename=None, memory=False, drop=False):
        self._engine = None
        self.session = None
        self._metadata = None
        self._setup(filename=filename, memory=memory, drop=drop)

    def _connect(self, dbapi_connection, connection_rec=None):
        """Enable load extension on connect. Event handler triggered
        by sqlalchemy"""
        dbapi_connection.enable_load_extension(True)
        self._load_extension(dbapi_connection)
        if connection_rec:
            pass

    def _load_extension(self, session):
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
            self._initialize_spatialite_db(session)

    def _setup(self, memory=False, filename=None, drop=False):
        """Setup a sqlalchemy connection to spatialite with the proper
        setup."""

        if memory:
            self._engine = sqlalchemy.create_engine('sqlite://', module=sqlite)
        else:
            filename = filename or self.DEFAULT_FILENAME
            self._engine = sqlalchemy.create_engine(
                'sqlite:///%s' % filename,
                module=sqlite,
                poolclass=sqlalchemy.pool.QueuePool,
                pool_size=1)
        sqlevent.listen(self._engine,
                        "first_connect",
                        lambda c, r: self._connect(c, r))
        self.session = orm.sessionmaker(bind=self._engine)()
        self._metadata = sqlalchemy.MetaData(self._engine)
        self._create_schema()
        if drop:
            self._metadata.drop_all()
        self._metadata.create_all(self._engine)

    def _create_schema(self):
        """Create and contains the model definition"""

        metadata = self._metadata

        orm.clear_mappers()
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

        event = sqlalchemy.Table(
            'catalogue_event', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at',
                              sqlalchemy.DateTime, default=datetime.now()),
            sqlalchemy.Column('source_key',
                              sqlalchemy.String(), nullable=False),
            sqlalchemy.Column('eventsource_id', sqlalchemy.Integer,
                              sqlalchemy.ForeignKey(
                    'catalogue_eventsource.id')))
        orm.Mapper(Event, event, properties={
                'eventsource': orm.relationship(EventSource,
                                                backref=orm.backref('events'))
                })
        geoalchemy.GeometryDDL(event)

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
            sqlalchemy.Column('absolute_error',
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
                                               geoalchemy.Point(2),
                                               nullable=False),
            sqlalchemy.Column('semi_minor_90error',
                              sqlalchemy.Float(),
                              nullable=True),
            sqlalchemy.Column('semi_major_90error',
                              sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('depth', sqlalchemy.Float(), nullable=False),
            sqlalchemy.Column('depth_error',
                              sqlalchemy.Float(), nullable=True))
        orm.Mapper(Origin, origin, properties={
                'eventsource': orm.relationship(
                    EventSource,
                    backref=orm.backref('origins')),
                'position': geoalchemy.GeometryColumn(origin.c.position)})
        geoalchemy.GeometryDDL(origin)

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
                    backref=orm.backref('metadatas'))})
        geoalchemy.GeometryDDL(measuremetadata)


def _initialize_spatialite_db(connection):
    """Initialize Spatialite Database. Needed only when a newly
    freshed database or a corrupted one have to be used"""

    connection.execute('SELECT InitSpatialMetaData()')
    try:
        connection.execute("INSERT INTO spatial_ref_sys"
                           "(srid, auth_name, auth_srid,"
                           " ref_sys_name, proj4text)"
                           "VALUES (4326, 'epsg', 4326, 'WGS 84',"
                           " '+proj=longlat "
                           "+ellps=WGS84 +datum=WGS84 +no_defs')")
    except sqlite.OperationalError:
        pass
