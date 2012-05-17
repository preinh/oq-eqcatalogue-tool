# Copyright (c) 2010-2012, GEM Foundation.
#
# EqCatalogueTool is free software: you can redistribute it and/or modify it
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
# along with EqCatalogueTool. If not, see <http://www.gnu.org/licenses/>.


import eqcatalogue.models as db


class EventManager(object):
    """
    Event object allows to query an earthquake catalogue.
    :param session: sqlalchemy session object.
    """

    def __init__(self, cat=None, queryset=None):
        self.cat = cat or db.CatalogueDatabase()
        self._session = self.cat.session
        self.queryset = queryset or self._session.query(db.Event).join(
            db.MagnitudeMeasure).join(db.Origin).join(db.Agency)

    @classmethod
    def clone_with_queryset(self, em, queryset):
        new_em = EventManager(em.cat, queryset)
        return new_em

    def all(self):
        return self.queryset.all()

    def count(self):
        return self.queryset.count()

    def before(self, time):
        """
        return EventManager.clone(self) which allows to get
        all events before a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        queryset = self.queryset.filter(db.Origin.time < time)

        return EventManager.clone_with_queryset(self, queryset)

    def after(self, time):
        """
        return EventManager.clone(self) which allows to get
        all events after a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """
        queryset = self.queryset.filter(db.Origin.time > time)

        return EventManager.clone_with_queryset(self, queryset)

    def between(self, time_lb, time_ub):
        """
        return EventManager.clone(self) which allows to get
        all events in a time range, inside the earthquake catalogue.
        :param time_lb: time range lower bound.
        :param time_ub: time range upper bound.
        """
        return self.after(time_lb).before(time_ub)

    def with_agency(self, agency):
        """
        return EventManager.clone(self) which allows to get
        all events with a specified agency, inside the earthquake catalogue.
        :param agency: agency name
        """
        queryset = self.queryset.filter(db.Agency.source_key == agency)
        return EventManager.clone_with_queryset(self, queryset)

    def with_agencies(self, *agency_name_list):
        """
        return EventManager.clone_with_queryset(self) which allows to get
        all events with a specified agency, inside the earthquake catalogue.
        :param *agency_name_list: a list of agency names
        """
        queryset = self.queryset.filter(
            db.Agency.source_key.in_(agency_name_list))
        return EventManager.clone_with_queryset(self, queryset)

    def with_magnitudes(self, *magnitudes):
        """
        return EventManager.clone_with_queryset(self) which allows to get
        all events which have the specified magnitudes,
        inside the earthquake catalogue.
        :param *magnitudes: a list containing  of magnitudes.
        """
        queryset = self.queryset

        for magnitude in magnitudes:
            queryset = queryset.filter(
            db.Event.measures.any(
                db.MagnitudeMeasure.scale == magnitude))
        return EventManager.clone_with_queryset(self, queryset)

    def within_polygon(self, polygon):
        """
        return EventManager.clone_with_queryset(self) which allows to get
        all events within a specified polygon,
        inside the earthquake catalogue.
        :param polygon: a polygon specified in wkt format.
        """
        queryset = self.queryset.filter(
            db.Origin.position.within(polygon))
        return EventManager.clone_with_queryset(self, queryset)

    def within_distance_from_point(self, point, distance):
        """
        return EventManager.clone_with_queryset(self) which allows to get
        all events within a specified distance from a point,
        inside the earthquake catalogue.
        :param point: a point specified in wkt format.
        :param distance: distance specified in meters (see srid 4326).
        """
        queryset = self.queryset.filter(
                "PtDistWithin(catalogue_origin.position, GeomFromText('%s', "
                "4326), %s)" % (point, distance))
        return EventManager.clone_with_queryset(self, queryset)
