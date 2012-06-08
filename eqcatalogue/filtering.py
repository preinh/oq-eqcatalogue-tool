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


class EventFilter(object):
    """
    Manage a list of event.
    :param cat: a Catalogue Database object
    :param queryset: the base queryset of events (defaults to all
    events), the eventmanager works on
    """

    def __init__(self, cat=None, queryset=None):
        self.cat = cat or db.CatalogueDatabase()
        self._session = self.cat.session
        self._queryset = queryset or self._session.query(db.Event).join(
            db.MagnitudeMeasure).join(db.Origin).join(db.Agency)

    @classmethod
    def clone_with_queryset(self, em, queryset):
        """Create another EventFilter with the same catalogue and
        initializing queryset with the passed one"""
        new_em = EventFilter(em.cat, queryset)
        return new_em

    def all(self):
        """Layer compat with SQLAlchemy Query object"""
        return self._queryset.all()

    def count(self):
        """Layer compat with SQLAlchemy Query object"""
        return self._queryset.count()

    def before(self, time):
        """
        return EventFilter.clone(self) which allows to get
        all events before a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        queryset = self._queryset.filter(db.Origin.time < time)

        return EventFilter.clone_with_queryset(self, queryset)

    def after(self, time):
        """
        return EventFilter.clone(self) which allows to get
        all events after a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        queryset = self._queryset.filter(db.Origin.time > time)

        return EventFilter.clone_with_queryset(self, queryset)

    def between(self, time_lb, time_ub):
        """
        return EventFilter.clone(self) which allows to get
        all events in a time range, inside the earthquake catalogue.
        :param time_lb: time range lower bound.
        :param time_ub: time range upper bound.
        """
        return self.after(time_lb).before(time_ub)

    def with_agency(self, agency):
        """
        return EventFilter.clone(self) which allows to get
        all events with a specified agency, inside the earthquake catalogue.
        :param agency: agency name
        """
        queryset = self._queryset.filter(db.Agency.source_key == agency)
        return EventFilter.clone_with_queryset(self, queryset)

    def with_agencies(self, *agency_name_list):
        """
        return EventFilter.clone_with_queryset(self) which allows to get
        all events with a specified agency, inside the earthquake catalogue.
        :param *agency_name_list: a list of agency names
        """
        queryset = self._queryset.filter(
            db.Agency.source_key.in_(agency_name_list))
        return EventFilter.clone_with_queryset(self, queryset)

    def with_magnitudes(self, *magnitudes):
        """
        return EventFilter.clone_with_queryset(self) which allows to get
        all events which have the specified magnitudes,
        inside the earthquake catalogue.
        :param *magnitudes: a list containing  of magnitudes.
        """
        queryset = self._queryset

        for magnitude in magnitudes:
            queryset = queryset.filter(
            db.Event.measures.any(
                db.MagnitudeMeasure.scale == magnitude))
        return EventFilter.clone_with_queryset(self, queryset)

    def within_polygon(self, polygon):
        """
        return EventFilter.clone_with_queryset(self) which allows to get
        all events within a specified polygon,
        inside the earthquake catalogue.
        :param polygon: a polygon specified in wkt format.
        """
        queryset = self._queryset.filter(
            db.Origin.position.within(polygon))
        return EventFilter.clone_with_queryset(self, queryset)

    def within_distance_from_point(self, point, distance):
        """
        return EventFilter.clone_with_queryset(self) which allows to get
        all events within a specified distance from a point,
        inside the earthquake catalogue.
        :param point: a point specified in wkt format.
        :param distance: distance specified in meters (see srid 4326).
        """
        queryset = self._queryset.filter(
                "PtDistWithin(catalogue_origin.position, GeomFromText('%s', "
                "4326), %s)" % (point, distance))
        return EventFilter.clone_with_queryset(self, queryset)

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
