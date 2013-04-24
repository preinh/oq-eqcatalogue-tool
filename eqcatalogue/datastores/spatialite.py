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
from eqcatalogue.models import MagnitudeMeasure

DLL_LIBRARY = "libspatialite.dll"
DYLIB_LIBRARY = "libspatialite.dylib"
SO_LIBRARY = "libspatialite.so.3"


class Engine(object):
    """
    The engine object responsible to map models object to spatialite
    database table.
    """
    DEFAULT_FILENAME = "eqcatalogue.db"

    def __init__(self, memory=False, filename=None, drop=False):
        """Setup a sqlalchemy connection to spatialite with the proper
        metadata.

        :param memory: if True the catalogue will use an in-memory
        database, otherwise a file-based database is used

        :param filename: the filename of the database used. Unused if
        `memory` is True

        :param drop: drop the content of the database
        """

        self.to_be_initialized = drop
        if memory:
            # set echo=True in debugging
            self._engine = sqlalchemy.create_engine('sqlite://', module=sqlite, echo=True)
            self.to_be_initialized = True
        else:
            filename = filename or self.DEFAULT_FILENAME
            if not os.path.exists(filename):
                self.to_be_initialized = True
            self._engine = sqlalchemy.create_engine(
                'sqlite:///%s' % filename,
                module=sqlite,
                poolclass=sqlalchemy.pool.QueuePool,
                pool_size=1)
        self.session = None
        self._metadata = None
        sqlevent.listen(self._engine, "first_connect", self._connect)
        self._engine.connect()
        while self.session is None:
            pass
        orm.clear_mappers()
        self._create_schema_magnitudemeasure()

        if self.to_be_initialized:
            self.recreate()

    def recreate(self):
        """
        Reset the database (both data and metadata)
        """
        self._metadata.drop_all()
        self._metadata.create_all(self._engine)

    def _create_schema_magnitudemeasure(self):
        """
        Create and contains the model definition. We used
        non-declarative model mapping, as we need to define models at
        runtime (not at module import time). Actually, only at runtime
        we can load the spatialite extension and then the spatialite
        metadata needed by geoalchemy to build the orm (s. #_setup
        method)"""

        metadata = self._metadata

        measure = sqlalchemy.Table(
            'catalogue_magnitudemeasure', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('created_at',
                              sqlalchemy.DateTime, default=datetime.now()),

            sqlalchemy.Column('event_source',
                              sqlalchemy.String(255), nullable=False),

            sqlalchemy.Column('event_key',
                              sqlalchemy.String(), nullable=False, index=True),
            sqlalchemy.Column('event_name',
                              sqlalchemy.String(), nullable=True),

            sqlalchemy.Column('agency',
                              sqlalchemy.String(), nullable=False, index=True),

            sqlalchemy.Column('origin_key',
                              sqlalchemy.String(), nullable=False, index=True),

            sqlalchemy.Column('time', sqlalchemy.DateTime,
                              nullable=False, index=True),
            sqlalchemy.Column('time_error', sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('time_rms', sqlalchemy.Float(), nullable=True),
            geoalchemy.GeometryExtensionColumn(
                'position', geoalchemy.Point(2, srid=4326), nullable=False),
            sqlalchemy.Column('semi_minor_90error',
                              sqlalchemy.Float(),
                              nullable=True),
            sqlalchemy.Column('semi_major_90error',
                              sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('depth', sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('depth_error',
                              sqlalchemy.Float(), nullable=True),
            sqlalchemy.Column('azimuth_error',
                              sqlalchemy.Float(),
                              nullable=True),
            sqlalchemy.Column('scale', sqlalchemy.String()),
            sqlalchemy.Column('value', sqlalchemy.Float(), index=True),
            sqlalchemy.Column('standard_error',
                              sqlalchemy.Float(),
                              nullable=True))

        orm.Mapper(MagnitudeMeasure, measure, properties={
            'position': geoalchemy.GeometryColumn(measure.c.position)})
        geoalchemy.GeometryDDL(measure)

    @staticmethod
    def position_from_latlng(latitude, longitude):
        """
        Given a `latitude` and a `longitude` returns a geoalchemy
        object suitable to be saved as geometry value
        """
        position = geoalchemy.WKTSpatialElement(
            'POINT(%s %s)' % (longitude, latitude))
        return position

    def _connect(self, dbapi_connection, _connection_rec=None):
        """Enable load extension on connect. Event handler triggered
        by sqlalchemy"""

        dbapi_connection.enable_load_extension(True)
        _load_extension(dbapi_connection)
        self.session = orm.sessionmaker(bind=self._engine)()
        self._metadata = sqlalchemy.MetaData(self._engine)


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
