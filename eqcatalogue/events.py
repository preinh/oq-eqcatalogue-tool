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
from sqlalchemy import and_


class Event(object):
    """
    Event object allows to query an earthquake catalogue.
    :param session: sqlalchemy session object.
    """

    def __init__(self, session):
        self.session = session

    def all(self):
        """
        Returns a query object which allows to get
        all events inside the earthquake catalogue.
        """

        return self.session.query(db.Event).join(db.MagnitudeMeasure).join(
            db.Origin)

    def before(self, time):
        """
        Returns a query object which allows to get
        all events before a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """

        return self.session.query(db.Event).join(db.MagnitudeMeasure).join(
            db.Origin).filter(db.Origin.time < time)

    def after(self, time):
        """
        Returns a query object which allows to get
        all events after a specified time, inside the earthquake catalogue.
        :param time: datetime object.
        """

        return self.session.query(db.Event).join(db.MagnitudeMeasure).join(
            db.Origin).filter(db.Origin.time > time)

    def between(self, time_lb, time_ub):
        """
        Returns a query object which allows to get
        all events in a time range, inside the earthquake catalogue.
        :param time_lb: time range lower bound.
        :param time_ub: time range upper bound.
        """

        return self.session.query(db.Event).join(db.MagnitudeMeasure).join(
            db.Origin).filter(and_(db.Origin.time >= time_lb,
            db.Origin.time <= time_ub))

    def with_agency(self, agency):
        """
        Returns a query object which allows to get
        all events with a specified agency, inside the earthquake catalogue.
        :param agency: agency name
        """

        return self.session.query(db.Event).join(db.MagnitudeMeasure).join(
            db.Agency).filter(db.Agency.source_key == agency)

    def with_magnitudes(self, magnitudes):
        """
        Returns a query object which allows to get
        all events which have the specified magnitudes,
        inside the earthquake catalogue.
        :param magnitudes: a list containing two types of magnitudes.
        """

        return self.session.query(db.Event).filter(
            db.Event.measures.any(
                db.MagnitudeMeasure.scale == magnitudes[0])).filter(
                db.Event.measures.any(db.MagnitudeMeasure.scale ==
                                      magnitudes[1]))

    def within_polygon(self, polygon):
        """
        Returns a query object which allows to get
        all events within a specified polygon,
        inside the earthquake catalogue.
        :param polygon: a polygon specified in wkt format.
        """

        return self.session.query(db.Event).join(db.MagnitudeMeasure).join(
                db.Origin).filter(db.Origin.position.within(polygon))

    #TODO
    def within_distance_from_point(self, point, distance):
        """
        Returns a query object which allows to get
        all events within a specified distance from a point,
        inside the earthquake catalogue.
        :param point: a point specified in wkt format.
        :param distance: distance specified in meters (see srid 4326).
        """

        return self.session.query(db.Event).join(db.MagnitudeMeasure).join(
                db.Origin).filter(db.Origin.position._within_distance
                    (point, distance))
