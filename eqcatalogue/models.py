from datetime import datetime

from pysqlite2 import dbapi2 as sqlite

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.events import event
from sqlalchemy.ext.declarative import declarative_base, declared_attr

import geoalchemy

Base = None
FILENAME = "eqcatalogue.db"

def connect(dbapi_connection, connection_rec):
    """Enable load extension on connect"""
    dbapi_connection.enable_load_extension(True)


# Create the spatialite database and load the schema
engine = sqlalchemy.create_engine('sqlite:///%s' % FILENAME, module=sqlite)
metadata = sqlalchemy.MetaData(engine)
Base = declarative_base(metadata=metadata)
event.listen(engine, "connect", connect)
session = orm.sessionmaker(bind=engine)()
try:
    session.execute("select load_extension('libspatialite.so')")
except sqlalchemy.exc.OperationalError:
    try:
        session.execute("select load_extension('libspatialite.dylib')")
    except sqlalchemy.exc.OperationalError:
        try:
            session.execute("select load_extension('libspatialite.dll')")
        except:
            raise RuntimeError("Could not load libspatial extension. Check your spatialite and pysqlite2 installation")

class BaseMixin(object):
    """A base class mixin to include for all the models. It provides the definition of the identifier and a timestamp.

    :py:attribute:: id
      Internal identifier

    :py:attribute:: created_at
      When this object has been imported into the catalogue db
      """

    @declared_attr
    def __tablename__(cls):
        return "catalogue_" + cls.__name__.lower()

    __table_args__ = {}
    __mapper_args__= {}

    id =  sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())

class CatalogueBaseMixin(BaseMixin):
    """A mixin for models that can have a local identifier (which can
    be different from the internal one) for each event source (e.g.
    solutionKey, eventKey)

    :py:attribute:: source_key
    the identifier used by the event source for the object
    """
    source_key = sqlalchemy.Column(sqlalchemy.String(), nullable=False)

    @declared_attr
    def eventsource_id(cls):
        return sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey('catalogue_eventsource.id'))

class EventSource(BaseMixin, Base):
    """A source of event catalogues. E.g. ISC Web Catalogue

    We assume that for each event source there is only one file format
we import data from

    :py:attribute:: name
    an unique event source short name.
    """

    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True)

    def __repr__(self):
        return "Event Source: %s" % self.name

class Agency(CatalogueBaseMixin, Base):
    """The agency which recorded and measured the events.

    :py:attribute:: name
    agency long name, short_name (e.g. ISC, IDC, DMN) should be saved
    into source_key

    :py:attribute:: eventsource
    the source object we have imported the agency from. It is unique
    together with `short_name`
"""
    name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)

    eventsource = orm.relationship("EventSource",
                                   backref=orm.backref('agencies'))

    def __repr__(self):
        if self.name:
            return "Agency %s (%s)" % (self.name, self.short_name)
        else:
            return "Agency %s" % self.short_name

class Event(CatalogueBaseMixin, Base):
    """Describes a sismic event.

    :py:attribute:: eventsource
    the source object we have imported the agency from. unique
    together with `source_key`
"""

    eventsource = orm.relationship("EventSource", backref=orm.backref('events'))

    def __repr__(self):
        return "Event %s (by %s)" % (self.source_key,
                                     self.source)

class MagnitudeMeasure(BaseMixin, Base):
    """Describes a single measure of the magnitude of an event

    :py:attribute:: event
    the event object associated with this measure

    :py:attribute:: agency
    the agency that has provided the measure

    :py:attribute:: origin
    the origin related to this measure

    :py:attribute:: scale
    the scale used for this measure. It is unique together with `agency_id` and `origin_id`

    :py:attribute:: value
    the magnitude expressed in the unit suitable for the scale used

    :py:attribute:: error
    the magnitude error (FIXME: please tell me if it is relative or absolute)

    """

    SCALES = ('mL', 'mb', 'Mb', 'Ms', 'md', 'MD', 'MS', 'mb1', 'mb1mx', 'ms1', 'ms1mx')

    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_event.id'))
    event = orm.relationship("Event", backref=orm.backref('measures'))

    agency_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_agency.id'))
    agency = orm.relationship("Agency", backref=orm.backref('measures'))

    origin_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_origin.id'))
    origin = orm.relationship("Origin", backref=orm.backref('measures'))

    scale = sqlalchemy.Enum(SCALES)
    value = sqlalchemy.Column(sqlalchemy.Float())

    absolute_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

    def __repr__(self):
        return "measure of %s at %s by %s: %s %s" % (self.event, self.origin, self.agency, self.scale, self.value)

class Origin(CatalogueBaseMixin, Base):
    """Describes a point at a given depth and a time. For each quantity a measure of the  accuracy is described.

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

    eventsource = orm.relationship("EventSource",
                                   backref=orm.backref('origins'))

    time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    time_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    time_rms = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

    position = geoalchemy.GeometryColumn(geoalchemy.Point(2), nullable=False)

    semi_minor_90error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    semi_major_90error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

    depth = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)

    depth_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

class MeasureMetadata(BaseMixin, Base):
    """Metadata of a measurement.

    :py:attribute:: magnitudemeasure
    the measure, the metadata is associated with

    :py:attribute:: name
    the name of the metadata. It is unique together with magnitudemeasure
    """

    METADATA_TYPES = ('phases', 'stations',
                      'azimuth_gap', 'azimuth_error',
                      'min_distance', 'max_distance',
                      'num_stations')

    magnitudemeasure_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_magnitudemeasure.id'))
    magnitudemeasure = orm.relationship("MagnitudeMeasure", backref=orm.backref('metadatas'))

    name = sqlalchemy.Enum(METADATA_TYPES, nullable=False)
    value = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)


def create_all():
    geoalchemy.GeometryDDL(Origin.__table__)
    Base.metadata.create_all(engine)

def recreate_all():
    try:
        Base.metadata.drop_all() # can fail if tables are not present
    except sqlalchemy.exc.OperationalError:
        pass
    create_all()
