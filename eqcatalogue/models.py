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
The module  provides the API to create and access
the database.

Moreover, it contains the class definitions of the basic domain models
stored into the db (eventsources, events, measures, origins and
measure metadata).
"""

import collections
from shapely import wkb
import numpy as np

from eqcatalogue import log
from sqlalchemy import func


DEFAULT_ENGINE = 'eqcatalogue.datastores.spatialite'


class MagnitudeMeasure(object):
    """
    Describes a single measure of the magnitude of an event

    :attribute id:
      Internal identifier

    :attribute datetime created_at:
      When this object has been imported into the catalogue db

    :attribute str agency:
      the identifier used by the event source for the Agency that has provided
      the measure

    :attribute str event_source:
      the source from which this measure has been imported

    :attribute event_key: the identifier used by the event
      source for the event. A same event could be related to different
      measures. Intensionally denormalized.

    :attribute event_name:
      a short name for the event. Same consideration as above

    :attribute origin:
      the origin related to this measure

    :attribute scale:
      the scale used for this measure.
      It is unique together with `agency_id` and `origin_id`

    :attribute value:
      the magnitude expressed in the unit suitable for the scale used

    :attribute standard_error:
      the standard error of the magnitude value

    :attribute time:
      Time in format "YYYY-MM-DD HH:MM:SS.SSS".

    :attribute time_error:
      Time errors expressed in seconds.

    :attribute time_rms:
      Time error expressed as a Root Mean Square in seconds.

    :attribute position:
      Point coordinate (latitude and longitude).
      You can create a point object by using the utility function
      `eqcatalogue.models.CatalogueDatabase.position_from_latlng`

    :attribute semi_major_90error:
      Semi-Major axis of the 90th percentile confidence ellipsis of the
      epicentre.

    :attribute semi_minor_90error:
      Semi-Minor axis of the 90th percentile confidence ellipsis of the
      epicentre.

    :attribute azimuth_error:
      Azimuth with respect to geographical north of the Semi-Major axis.

    :attribute depth:
      depth of the hypocentre in km.

    :attribute depth_error:
      Error in km on the hypocentre depth.
    """

    def __init__(self,
                 time,
                 position,
                 scale,
                 value,
                 origin_key=None,
                 agency=None,
                 event_source=None,
                 event_key=None,
                 event_name=None,
                 standard_error=None,
                 semi_minor_90error=None,
                 semi_major_90error=None,
                 depth_error=None,
                 time_rms=None,
                 azimuth_error=None,
                 time_error=None,
                 depth=None):
        self.id = None
        self.agency = agency
        self.event_source = event_source
        self.event_key = event_key
        self.origin_key = origin_key
        self.event_name = event_name
        self.scale = scale
        self.value = value
        self.standard_error = standard_error
        self.semi_minor_90error = semi_minor_90error
        self.semi_major_90error = semi_major_90error
        self.depth_error = depth_error
        self.time_rms = time_rms
        self.azimuth_error = azimuth_error
        self.time_error = time_error
        self.depth = depth
        self.time = time
        self.position = position

    def __repr__(self):
        if self.position is not None:
            return "%s %s (sigma=%s) @ %s-%s" % (
                self.value, self.scale, self.standard_error,
                self.position_as_tuple(), self.time)
        else:
            return "%s %s (sigma=%s) at %s" % (
                self.value, self.scale, self.standard_error, self.time)

    def keys(self):
        return ["id", "agency", "event", "origin",
                "scale", "value", "standard_error"]

    def values(self):
        if self.standard_error:
            stderr = "%.4f" % self.standard_error
        else:
            stderr = ""

        return [self.id, self.agency,
                self.event_key, self.origin_key,
                self.scale, "%.4f" % self.value, stderr]

    def time_distance(self, measure):
        return abs(self.time - measure.time).total_seconds()

    def magnitude_distance(self, measure):
        return abs(self.value - measure.value)

    def space_distance(self, measure):
        """
        calculate geographical distance using the haversine formula.
        """

        earth_rad = 6371.227
        coords = self.position_as_tuple() + measure.position_as_tuple()

        # convert to radians
        lon1, lat1, lon2, lat2 = [c * np.pi / 180 for c in coords]

        dlat, dlon = lat1 - lat2, lon1 - lon2
        aval = (np.sin(dlat / 2.) ** 2. +
                np.cos(lat1) * np.cos(lat2) * (np.sin(dlon / 2.) ** 2.))
        distance = (2. * earth_rad *
                    np.arctan2(np.sqrt(aval), np.sqrt(1 - aval)))

        return distance

    @classmethod
    def make_from_lists(cls, scale, values, sigmas):
        """
        Returns a list of measures with the given scale, values and
        standard errors
        """
        return [cls(time=None, position=None,
                    scale=scale, value=v[0], standard_error=v[1])
                for v in zip(values, sigmas)]

    def position_as_tuple(self):
        if hasattr(self.position, 'geom_wkb'):
            geom = wkb.loads(str(self.position.geom_wkb))
            return geom.x, geom.y
        else:
            return self.position.coords(0)

    def convert(self, new_value, formula, standard_error):
        """
        Convert the measure to a ConvertedMeasure with `new_value`
        through `formula`
        """
        return ConvertedMeasure(
            event_source=self.event_source,
            event_key=self.event_key,
            agency=self.agency,
            origin_key=self.origin_key,
            time=self.time,
            position=self.position,
            scale=formula.target_scale,
            value=new_value,
            event_name=self.event_name,
            standard_error=standard_error,
            semi_minor_90error=self.semi_minor_90error,
            semi_major_90error=self.semi_major_90error,
            depth_error=self.depth_error,
            time_rms=self.time_rms,
            azimuth_error=self.azimuth_error,
            time_error=self.time_error,
            depth=self.depth,
            original_measure=self,
            formulas=[formula])


class ConvertedMeasure(object):
    """
    A converted measure is measure that is the result of a conversion
    """
    def __init__(self,
                 time,
                 position,
                 scale,
                 value,
                 original_measure,
                 formulas,
                 event_source=None,
                 event_key=None,
                 agency=None,
                 origin_key=None,
                 event_name=None,
                 standard_error=None,
                 semi_minor_90error=None,
                 semi_major_90error=None,
                 depth_error=None,
                 time_rms=None,
                 azimuth_error=None,
                 time_error=None,
                 depth=None):
        # we do not inherit by MagnitudeMeasure because it could be
        # sqlalchemizable, and, consenquently it may have some magic
        # in the constructor that we don't want here

        self.id = None
        self.agency = agency
        self.event_source = event_source
        self.event_key = event_key
        self.origin_key = origin_key
        self.event_name = event_name
        self.scale = scale
        self.value = value
        self.standard_error = standard_error
        self.semi_minor_90error = semi_minor_90error
        self.semi_major_90error = semi_major_90error
        self.depth_error = depth_error
        self.time_rms = time_rms
        self.azimuth_error = azimuth_error
        self.time_error = time_error
        self.depth = depth
        self.time = time
        self.position = position
        self.original_measure = original_measure
        self.formulas = formulas or []

    def __repr__(self):
        return "%s %s (sigma=%s) converted by %s" % (
            self.value, self.scale, self.standard_error,
            self.original_measure)

    def keys(self):
        return ["agency", "event", "origin",
                "scale", "value", "standard_error",
                "original_measure", "formulas"]

    def values(self):
        if self.standard_error:
            stderr = "%.4f" % self.standard_error
        else:
            stderr = ""
        return [self.agency,
                self.event_key, self.origin_key,
                self.scale, "%.4f" % self.value, stderr,
                self.original_measure, ".".join(f.name for f in self.formulas)]

    def convert(self, new_value, formula, standard_error):
        """
        Convert the measure to a ConvertedMeasure with `new_value`
        and `standard_error` through `formula`.
        """
        return self.__class__(
            event_source=self.event_source,
            event_key=self.event_key,
            agency=self.agency,
            origin_key=self.origin_key,
            time=self.time,
            position=self.position,
            scale=formula.target_scale,
            value=new_value,
            event_name=self.event_name,
            standard_error=standard_error,
            semi_minor_90error=self.semi_minor_90error,
            semi_major_90error=self.semi_major_90error,
            depth_error=self.depth_error,
            time_rms=self.time_rms,
            azimuth_error=self.azimuth_error,
            time_error=self.time_error,
            depth=self.depth,
            original_measure=self.original_measure,
            formulas=self.formulas[:] + [formula])


class Workspace(type):
    """Metaclass to implement a modified singleton pattern. The
    singleton instance is actually created the first time and whenever
    at least an argument have been passed to the default constructor,
    otherwise the current instance is returned."""
    def __init__(mcs, name, bases, der):
        super(Workspace, mcs).__init__(name, bases, der)
        mcs.instance = None

    def __call__(mcs, *args, **kw):
        if args or kw or not mcs.instance:
            if mcs.instance:
                mcs.instance.close()
            mcs.instance = super(Workspace, mcs).__call__(*args, **kw)
        return mcs.instance


class CatalogueDatabase(object):
    """
    This is the main class used to access the database of measures,
    events, etc.

    :keyword drop:
      Drop and recreate the database after opening

    :param engine_class_module:
      A module that implements an engine protocol.
      If not provided, the default is eqcatalogue.datastores.spatialite

    Any other params is passed to the engine constructor.
    For spatialite, you have the following keyword arguments:

    :keyword memory:
      Open an in-memory database
    :type memory: Boolean
    :keyword filename:
      Open a file database located at path `filename`. If not given, the
      default is `eqcatalogue.db`
    :type filename: string

    e.g.::
      cat = CatalogueDatabase(filename="my-catalogue.db")
    """

    __metaclass__ = Workspace
    MEASURE_AGENCIES = 'available_measure_agencies'
    MEASURE_SCALES = 'available_measure_scales'

    def __init__(self, engine=DEFAULT_ENGINE, **engine_params):
        log.logger(__name__).info(
            "initializing Catalogue Database (engine=%s, params %s)",
            engine, engine_params)
        self._engine_class = self.__class__.get_engine(engine)
        self._engine = self._engine_class(**engine_params)
        if 'drop' in engine_params or 'memory' in engine_params:
            log.logger(__name__).info("reset catalogue data")
        self._cache = collections.defaultdict(dict)

    def recreate(self):
        """
        Recreate the database. It destroys all the data and recreate
        the schema.
        """
        self._engine.recreate()

    def close(self):
        """
        Reset the singleton, allowing to switch between different databases
        """
        self.session.close()

    @classmethod
    def get_engine(cls, module_name):
        """
        Return the Engine class that is defined into `module_name`
        """
        module = __import__(module_name, fromlist=['Engine'])
        return module.Engine

    @property
    def session(self):
        """
        Return the current CatalogueDatabase session
        """
        return self._engine.session

    def load_file(self, filename, importer_module_name, **kwargs):
        """
        Load filename by using an Importer defined in
        `importer_module_name`. Other kwargs are passed to the store
        method of the importer
        """
        if not '.' in importer_module_name:
            importer_module_name = (
                'eqcatalogue.importers.' + importer_module_name)
        module = __import__(importer_module_name, fromlist=['Importer'])
        importer = module.Importer(file(filename), self)
        summary = importer.store(**kwargs)
        log.logger(__name__).info(summary)

    def position_from_latlng(self, latitude, longitude):
        """
        Utility function to create a POINT object suitable to be stored
        into :class:`eqcatalogue.models.Origin.position`
        """
        return self._engine_class.position_from_latlng(latitude, longitude)

    def get_agencies(self):
        """
        Returns a set containing the measure agencies.
        """

        query = self.session.query(MagnitudeMeasure).distinct()
        return set([m.agency for m in query])

    def get_measure_scales(self):
        """
        Returns a set containing the measure scales.
        """

        available_scales = [magnitude_measure.scale
                            for magnitude_measure in
                            self.session.query(MagnitudeMeasure).all()]
        return set(available_scales)

    def get_dates(self):
        """
        Returns a tuple with minimum and maximum date
        """

        date_min = self.session.query(
            func.min(MagnitudeMeasure.time)).first()[0]
        date_max = self.session.query(
            func.max(MagnitudeMeasure.time)).first()[0]
        return date_min, date_max

    def get_summary(self):
        """
        Returns a summary dict with informations related
        to the available measure agencies and scales.
        """

        return {self.__class__.MEASURE_AGENCIES:
                self.get_agencies(),
                self.__class__.MEASURE_SCALES:
                self.get_measure_scales()}
