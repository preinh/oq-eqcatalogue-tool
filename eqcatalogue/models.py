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


"""Create the spatialite database and load the schema"""
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
    """A base class to inherit from for catalogue models"""

    @declared_attr
    def __tablename__(cls):
        return "catalogue_" + cls.__name__.lower()

    __table_args__ = {}
    __mapper_args__= {}

    "Internal identifier"
    id =  sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    "When this objects has been imported into the catalogue db"
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())

class CatalogueBaseMixin(BaseMixin):
    """A base class for models that can have an identifier (which can
    be different from the internal one) local for each source"""

    "the identifier used by the event source for the object"
    source_key = sqlalchemy.Column(sqlalchemy.String(), nullable=False)

class EventSource(BaseMixin, Base):
    """A source of event catalogues. E.g. ISC Web Catalogue"""

    "event short description."
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True)

    def __repr__(self):
        return "EventSource: %s" % self.name

class Agency(BaseMixin, Base):
    """The agency which recorded and measured the events"""

    # agency short name. e.g. ISC, IDC, DMN
    short_name = sqlalchemy.Column(sqlalchemy.String(255))

    # agency long name.
    name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)

    eventsource_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_eventsource.id'))
    eventsource = orm.relationship("Source", backref=orm.backref('agencies', order_by='created_at'))

    # unique together (eventsource_id and short_name)

    def __repr__(self):
        if self.name:
            return "Agency %s (%s)" % (self.name, self.short_name)
        else:
            return "Agency %s" % self.short_name

class Event(CatalogueBaseMixin, Base):
    """Describes an event"""

    eventsource_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_eventsource.id'))
    eventsource = orm.relationship("Source", backref=orm.backref('events', order_by='created_at'))
    # unique togethr (source_key and eventsource_id)

    def __repr__(self):
        return "Event %s (by %s)" % (self.source_key,
                                     self.source)

class MagnitudeMeasure(BaseMixin, Base):
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_event.id'))
    event = orm.relationship("Event", backref=orm.backref('measures', order_by=id))

    agency_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_agency.id'))
    agency = orm.relationship("Agency", backref=orm.backref('measures', order_by=id))

    origin_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_origin.id'))
    origin = orm.relationship("Origin", backref=orm.backref('measures', order_by=id))

    scale = sqlalchemy.Column(sqlalchemy.String())
    value = sqlalchemy.Column(sqlalchemy.Float())

    absolute_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

    # unique together (scale, agency_id and origin_id)

    def __repr__(self):
        return "measure of event %s (origin: %s, time: %s"

class Origin(BaseMixin, Base):
    time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    time_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    time_rms = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

    position = geoalchemy.GeometryColumn(geoalchemy.Point(2))
    semi_minor_90error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    semi_major_90error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    azimuth_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

    depth = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)
    depth_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)

class MeasureMetadata(BaseMixin, Base):
    magnitudemeasure_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_magnitudemeasure.id'))
    magnitudemeasure = orm.relationship("MagnitudeMeasure", backref=orm.backref('metadatas', order_by='name'))

    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    value = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)

    # unique_together(measure_id, name)


Base.metadata.create_all(engine)
