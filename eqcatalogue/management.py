from datetime import datetime

from pysqlite2 import dbapi2 as sqlite

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.events import event
from sqlalchemy.ext.declarative import declarative_base

import geoalchemy

Base = None

def connect(dbapi_connection, connection_rec):
    """Enable load extension on connect"""
    dbapi_connection.enable_load_extension(True)

def createdb(filename = "eqcatalogue.db", engine_args=None):
    """Create the spatialite database and load the schema"""
    engine_args = engine_args or {}
    engine_args.update({'module': sqlite})

    engine = sqlalchemy.create_engine('sqlite:///%s' % filename, **engine_args)
    metadata = sqlalchemy.MetaData(engine)
    Base = declarative_base(metadata=metadata)
    # we can import models only after that Base has been defined
    import models

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

    Base.metadata.create_all(engine)
