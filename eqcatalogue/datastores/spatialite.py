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
Engine for eqcatalogue tool using spatialite database and geoalchemy
as ORM wrapper
"""

import os
from datetime import datetime
from pysqlite2 import dbapi2 as sqlite
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.events import event as sqlevent
import geoalchemy
from eqcatalogue.models import (EventSource, Event, MagnitudeMeasure, Agency,
                                Origin, MeasureMetadata, METADATA_TYPES)

DLL_LIBRARY = "libspatialite.dll"
DYLIB_LIBRARY = "libspatialite.dylib"
SO_LIBRARY = "libspatialite.so.3"


class Engine(object):
    """
    The engine object responsible to map models object to spatialite
    database table.
    """
    DEFAULT_FILENAME = "eqcatalogue.db"

    def __init__(self, memory=False, filename=None):
        """Setup a sqlalchemy connection to spatialite with the proper
        metadata.

        :param memory: if True the catalogue will use an in-memory
        database, otherwise a file-based database is used

        :param filename: the filename of the database used. Unused if
        `memory` is True
        """

        to_be_initialized = False
        if memory:
            self._engine = sqlalchemy.create_engine('sqlite://', module=sqlite)
            to_be_initialized = True
        else:
            filename = filename or self.DEFAULT_FILENAME
            if not os.path.exists(filename):
                to_be_initialized = True
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
        if to_be_initialized:
            self.recreate()

    def recreate(self):
        """
        Reset the database (both data and metadata)
        """
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
                              sqlalchemy.String(), nullable=False, index=True),
            sqlalchemy.Column('eventsource_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey(
                    'catalogue_eventsource.id'),
                    nullable=False))
        orm.Mapper(Agency, agency, properties={
                'eventsource': orm.relationship(
                    EventSource,
                    lazy='noload',
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
                              sqlalchemy.String(), nullable=False, index=True),
            sqlalchemy.Column('name',
                              sqlalchemy.String(), nullable=True),
            sqlalchemy.Column('eventsource_id', sqlalchemy.Integer,
                              sqlalchemy.ForeignKey(
                    'catalogue_eventsource.id'),
                    nullable=False))
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
                              sqlalchemy.ForeignKey('catalogue_event.id'),
                              nullable=False),
            sqlalchemy.Column('agency_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey('catalogue_agency.id'),
                              nullable=False),
            sqlalchemy.Column('origin_id',
                              sqlalchemy.Integer,
                              sqlalchemy.ForeignKey('catalogue_origin.id'),
                              nullable=False),
            sqlalchemy.Column('scale', sqlalchemy.String()),
            sqlalchemy.Column('value', sqlalchemy.Float(), index=True),
            sqlalchemy.Column('standard_error',
                              sqlalchemy.Float(),
                              nullable=True))

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
                                  'catalogue_eventsource.id'),
                              nullable=False),
            sqlalchemy.Column('time', sqlalchemy.DateTime,
                              nullable=False, index=True),
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
            'position': geoalchemy.GeometryColumn(
                origin.c.position)})
        geoalchemy.GeometryDDL(origin)

    def _create_schema_measuremetadata(self):
        """Create the schema for the measure metadata model"""

        metadata = self._metadata

        measuremetadata = sqlalchemy.Table(
            'catalogue_measuremetadata', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at', sqlalchemy.DateTime,
                              default=datetime.now()),
            sqlalchemy.Column(
                'magnitudemeasure_id', sqlalchemy.Integer,
                sqlalchemy.ForeignKey(
                    'catalogue_magnitudemeasure.id'),
                nullable=False),
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
        """
        Create and contains the model definition. We used
        non-declarative model mapping, as we need to define models at
        runtime (not at module import time). Actually, only at runtime
        we can load the spatialite extension and then the spatialite
        metadata needed by geoalchemy to build the orm (s. #_setup
        method)
        """

        orm.clear_mappers()

        self._create_schema_eventsource()
        self._create_schema_agency()
        self._create_schema_event()
        self._create_schema_magnitudemeasure()
        self._create_schema_origin()
        self._create_schema_measuremetadata()

    @staticmethod
    def position_from_latlng(latitude, longitude):
        """
        Given a `latitude` and a `longitude` returns a geoalchemy
        object suitable to be saved as geometry value
        """
        position = geoalchemy.WKTSpatialElement(
            'POINT(%s %s)' % (longitude, latitude))
        return position


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

    # FIXME: This is a workaround to load the spatialite library. We
    # guess different filename for the spatialite extension and use a
    # variable as a sentinel. The exceptions raised are saved in the
    # variable exception for further printing/logging
    exceptions, loaded = {}, False
    for library in [SO_LIBRARY, DLL_LIBRARY, DYLIB_LIBRARY]:
        try:
            session.execute("select load_extension('%s')" % library)
            loaded = True
        except sqlite.OperationalError as e:
            exceptions[library] = e

    if not loaded:
        raise RuntimeError("""
    Could not load libspatial extension.
    Check your spatialite and pysqlite2 installation
    Errors %s""" % exceptions)

    # spatialite needs this initialization on the first usage. This
    # should be probably go into a package installation script
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
