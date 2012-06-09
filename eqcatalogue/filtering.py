# Copyright (c) 2010-2012, GEM Foundation.
#
# eqcataloguetool is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EqCatalogueTool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with eqcataloguetool. If not, see <http://www.gnu.org/licenses/>.

"""
Tools to filter events and measures
"""

import eqcatalogue.models as db


class MeasureFilter(object):
    """
    Allow to filter the measures in a catalogue database

    :param cat: a Catalogue Database object
    """

    def __init__(self, cat=None, queryset=None):
        self.cat = cat or db.CatalogueDatabase()
        self._session = self.cat.session
        self.queryset = queryset or self._session.query(
            db.MagnitudeMeasure).join(db.Origin).join(db.Agency)

    def _clone_with_queryset(self, queryset):
        """Create another MeasureFilter with the same catalogue and
        initializing queryset with the passed one"""
        new_m = MeasureFilter(self.cat, queryset)
        return new_m

    def all(self):
        """Layer compat with SQLAlchemy Query object"""
        return self.queryset.all()

    def count(self):
        """Layer compat with SQLAlchemy Query object"""
        return self.queryset.count()

    def combine(self, measure_filter):
        return self._clone_with_queryset(measure_filter.queryset)

    def events(self):
        """Return all the distinct events associated with all the
        measures"""
        subquery = self.queryset.subquery()
        return self.cat.session.query(db.Event).join(subquery).all()

    def before(self, time):
        """
        return MeasureFilter._clone(self) which allows to get
        all measures before a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        queryset = self.queryset.filter(db.Origin.time < time)

        return self._clone_with_queryset(queryset)

    def after(self, time):
        """
        return MeasureFilter._clone(self) which allows to get
        all measures after a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        queryset = self.queryset.filter(db.Origin.time > time)

        return self._clone_with_queryset(queryset)

    def between(self, time_lb, time_ub):
        """
        return MeasureFilter._clone(self) which allows to get
        all measures in a time range, inside the earthquake catalogue.
        :param time_lb: time range lower bound.
        :param time_ub: time range upper bound.
        """
        return self.after(time_lb).before(time_ub)

    def filter(self, *filter_args, **filter_kwargs):
        """
        Generic SQLAlchemy filter wrapper. Returns a _clone of the
        current measures filtered by filter_args and filter_kwargs.
        They can be any filter that you can pass to a SQLAlchemy Query
        object
        """
        queryset = self.queryset.filter(*filter_args, **filter_kwargs)
        return self._clone_with_queryset(queryset)

    def with_agencies(self, *agency_name_list):
        """
        return MeasureFilter._clone_with_queryset(self) which allows to get
        all measures with a specified agency, inside the earthquake catalogue.
        :param *agency_name_list: a list of agency names
        """
        queryset = self.queryset.filter(
            db.Agency.source_key.in_(agency_name_list))
        return self._clone_with_queryset(queryset)

    def with_magnitude_scales(self, *scales):
        """
        return a MeasureFilter with all the measures which have one of
        the specified magnitude scales inside the earthquake
        catalogue.
        :param *scales: a list of magnitude scales.
        """
        queryset = self.queryset.filter(
                db.MagnitudeMeasure.scale.in_(scales))
        return self._clone_with_queryset(queryset)

    def within_polygon(self, polygon):
        """
        return MeasureFilter._clone_with_queryset(self) which allows to get
        all measures within a specified polygon,
        inside the earthquake catalogue.
        :param polygon: a polygon specified in wkt format.
        """
        queryset = self.queryset.filter(
            db.Origin.position.within(polygon))
        return self._clone_with_queryset(queryset)

    def within_distance_from_point(self, point, distance):
        """
        return MeasureFilter._clone_with_queryset(self) which allows to get
        all measures within a specified distance from a point,
        inside the earthquake catalogue.
        :param point: a point specified in wkt format.
        :param distance: distance specified in meters (see srid 4326).
        """
        queryset = self.queryset.filter(
                "PtDistWithin(catalogue_origin.position, GeomFromText('%s', "
                "4326), %s)" % (point, distance))
        return self._clone_with_queryset(queryset)

    def group_measures(self, grouping_strategy=None):
        """
        Group all measures by event :param grouping_strategy: a
        function that returns a dictionary where the key identifies an
        event, and the value stores a list of measures
        """
        if not grouping_strategy:
            from eqcatalogue.grouping import GroupMeasuresByEventSourceKey
            grouping_strategy = GroupMeasuresByEventSourceKey()
        return grouping_strategy.group_measures(self)


class EventFilter(object):
    """
    Allow to filter the measures in a catalogue database
    :param cat: a Catalogue Database object
    """

    def __init__(self, cat=None, measure_filter=None):
        self.cat = cat or db.CatalogueDatabase()
        if measure_filter:
            self.measure_filter = MeasureFilter(self.cat,
                                                measure_filter.queryset)
        else:
            self.measure_filter = MeasureFilter(self.cat)

    def __clone_with_measures(self, measure_filter):
        """Create another EventFilter with the same catalogue and
        initializing queryset with the passed one"""
        new_em = EventFilter(self.cat, measure_filter)
        return new_em

    def all(self):
        """Returns a list with the filtered events"""
        return self.measure_filter.events()

    def count(self):
        """Returns the number of filtered events"""
        return len(self.all())

    def before(self, time):
        """
        return EventFilter._clone(self) which allows to get
        all events before a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        measure_filter = self.measure_filter.before(time)
        return self.__clone_with_measures(measure_filter)

    def after(self, time):
        """
        return EventFilter._clone(self) which allows to get
        all events after a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        measure_filter = self.measure_filter.after(time)
        return self.__clone_with_measures(measure_filter)

    def between(self, time_lb, time_ub):
        """
        return EventFilter._clone(self) which allows to get
        all events in a time range, inside the earthquake catalogue.
        :param time_lb: time range lower bound.
        :param time_ub: time range upper bound.
        """
        measure_filter = self.measure_filter.between(time_lb, time_ub)
        return self.__clone_with_measures(measure_filter)

    def with_agencies(self, *agency_name_list):
        """
        return EventFilter._clone_with_queryset(self) which allows to get
        all events with a specified agency, inside the earthquake catalogue.
        :param *agency_name_list: a list of agency names
        """
        measure_filter = self.measure_filter.with_agencies(
            *agency_name_list)
        return self.__clone_with_measures(measure_filter)

    def with_magnitude_scales(self, *scales):
        """
        return a list of events which have at least one of the
        specified magnitude scales, inside the earthquake catalogue.
        :param *magnitudes: a list containing of magnitude scales.
        """
        measure_filter = self.measure_filter.with_magnitude_scales(*scales)
        return self.__clone_with_measures(measure_filter)

    def within_polygon(self, polygon):
        """
        return EventFilter._clone_with_queryset(self) which allows to get
        all events within a specified polygon,
        inside the earthquake catalogue.
        :param polygon: a polygon specified in wkt format.
        """
        measure_filter = self.measure_filter.within_polygon(polygon)
        return self.__clone_with_measures(measure_filter)

    def within_distance_from_point(self, point, distance):
        """
        return EventFilter._clone_with_queryset(self) which allows to get
        all events within a specified distance from a point,
        inside the earthquake catalogue.
        :param point: a point specified in wkt format.
        :param distance: distance specified in meters (see srid 4326).
        """
        measure_filter = self.measure_filter.within_distance_from_point(
            point, distance)
        return self.__clone_with_measures(measure_filter)

    def group_measures(self, grouping_strategy=None):
        """
        Group all measures by event :param grouping_strategy: a
        function that returns a dictionary where the key identifies an
        event, and the value stores a list of measures
        """
        return self.measure_filter.group_measures(grouping_strategy)

    def measures(self):

        """Returns all the measures associated to the filtered
        events"""
        return self.measure_filter.all()
