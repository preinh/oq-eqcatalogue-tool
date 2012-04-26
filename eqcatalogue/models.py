from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import orm

from management import Base

if not Base:
    raise RuntimeError("Do not import this module until the engine metadata has not been defined and augmented with spatialite data")

class BaseMixin(object):
    """A base class to inherit from for catalogue models"""

    @declared_attr
    def __tablename__(cls):
        return "catalogue_" + cls.__name__.lower()

    __table_args__ = {}
    __mapper_args__= {}

    "Internal identifier"
    id =  sqlalchemy.Column(Integer, primary_key=True)

    "When this objects has been imported into the catalogue db"
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())

class CatalogueBaseMixin(BaseMixin):
    """A base class for models that can have an identifier (which can
    be different from the internal one) local for each source"""

    "the identifier used by the source for the object"
    catalogue_key = sqlalchemy.Column(sqlalchemy.String(), nullable=False)

class EventSource(BaseMixin, Base):
    """A source of event catalogues. E.g. ISC Web Catalogue"""

    "event short description."
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True)

class Agency(BaseMixin, Base):
    """The agency which recorded and measured the events"""

    # agency short name. e.g. ISC, IDC, DMN
    short_name = sqlalchemy.Column(sqlalchemy.String(255))

    # agency long name.
    name = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)

    source_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_source.id'))
    source = orm.relationship("Source", backref=orm.backref('events', order_by=created_at))

    # unique together (source_id e short_name)

class Event(CatalogueBaseMixin, Base):
    """Describes an event"""

    source_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_source.id'))
    source = orm.relationship("Source", backref=orm.backref('events', order_by=created_at))
    # catalogue_key e source_id sono unici together

class MagnitudeMeasure(CatalogueBaseMixin, Base):
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_event.id'))
    event = orm.relationship("Event", backref=orm.backref('events', order_by=id))

    agency_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_agency.id'))
    agency = orm.relationship("Agency", backref=orm.backref('measures', order_by=id))

    origin_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_solution.id'))
    origin = orm.relationship("Solution", backref=orm.backref('measures', order_by=id))

    scale = sqlalchemy.Column(sqlalchemy.String())
    value = sqlalchemy.Column(sqlalchemy.Float())

    error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

    # unique together (scale, agency_id and origin_id)

class Origin(BaseMixin, Base):
    time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    position = geoalchemy.GeometryColumn(geoalchemy.Point(2))
    depth = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)

    time_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    time_rms = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    semi_minor_90error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    semi_major_90error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)
    azimuth_error = sqlalchemy.Column(sqlalchemy.Float(), nullable=True)

class MeasureMetadata(BaseMixin, Base):
    measure_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalogue_measure.id'))
    measure = orm.relationship("Agency", backref=orm.backref('metadatas', order_by=name))

    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    value = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)

    # measure_id e name unique together



