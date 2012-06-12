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
Module :mod:`eqcatalogue.filtering` defines
:class:`MeasureFilter`.
"""

import eqcatalogue.models as db


class MeasureFilter(object):
    """
    Allows to filter measures stored in a catalogue database,
    by applying one or more filters. Filters can be chained
    together as method calls:
    MeasureFilter().after(time).within_polygon(polygon).

    :param cat: a Catalogue Database object.
    :param queryset: a Queryset instance of `sqlalchemy.orm.query.Query`.
    """

    def __init__(self, cat=None, queryset=None):
        self.cat = cat or db.CatalogueDatabase()
        self._session = self.cat.session
        self.queryset = queryset or self._session.query(
            db.MagnitudeMeasure).join(db.Origin).join(db.Agency)

    def _clone_with_queryset(self, queryset):
        """
        Returns a MeasureFilter instance with the same catalogue and
        initializing queryset with the passed one.
        """

        new_m = MeasureFilter(self.cat, queryset)
        return new_m

    def all(self):
        """
        Returns all the measures available in the queryset as a list.
        """

        return self.queryset.all()

    def count(self):
        """
        Returns a count of the rows that the queryset would return.
        """

        return self.queryset.count()

    def combine(self, measure_filter):
        """
        Returns a MeasureFilter instance which is the result of
        a combination with the one provided.

        :param measure_filter: A MeasureFilter instance to be combined.
        """

        return self._clone_with_queryset(measure_filter.queryset)

    def events(self):
        """
        Returns all the distinct events associated with all the
        measures, available in the queryset as a list.
        """

        subquery = self.queryset.subquery()
        return self.cat.session.query(db.Event).join(subquery).all()

    def before(self, time):
        """
        Returns all the measures before a specified time, available
        in the queryset as a list.

        :param time: datetime object.
        """

        queryset = self.queryset.filter(db.Origin.time < time)
        return self._clone_with_queryset(queryset)

    def after(self, time):
        """
        Returns all the measures after a specified time, available
        in the queryset as a list.

        :param time: datetime object.
        """

        queryset = self.queryset.filter(db.Origin.time > time)
        return self._clone_with_queryset(queryset)

    def between(self, time_lb, time_ub):
        """
        Returns all the measures within a time range, available
        in the queryset as a list.

        :param time_lb: time range lower bound.
        :param time_ub: time range upper bound.
        """

        return self.after(time_lb).before(time_ub)

    def filter(self, *filter_args, **filter_kwargs):
        """
        Returns all the measures, available in the queryset as a
        list. This method is a SQLAlchemy filter wrapper.
        """

        queryset = self.queryset.filter(*filter_args, **filter_kwargs)
        return self._clone_with_queryset(queryset)

    def with_agencies(self, *agency_name_list):
        """
        Returns all the measures which have one of the defined agencies,
        available in the queryset as a list.

        :param agency_name_list: a list of agency names
        """

        queryset = self.queryset.filter(
            db.Agency.source_key.in_(agency_name_list))
        return self._clone_with_queryset(queryset)

    def with_magnitude_scales(self, *scales):
        """
        Returns all the measures which have one of the specified magnitude
        scales, available in the queryset as a list.

        :param scales: a list of magnitude scales.
        """

        queryset = self.queryset.filter(
                db.MagnitudeMeasure.scale.in_(scales))
        return self._clone_with_queryset(queryset)

    def within_polygon(self, polygon):
        """
        Returns all the measures within a specified polygon, available
        in the queryset as a list.

        :param polygon: a polygon specified in wkt format.
        """

        queryset = self.queryset.filter(
            db.Origin.position.within(polygon))
        return self._clone_with_queryset(queryset)

    def within_distance_from_point(self, point, distance):
        """
        Returns all measures within a specified distance from a point,
        available in the queryset as a list.

        :param point: a point specified in wkt format.
        :param distance: distance specified in meters (see srid 4326).
        """

        queryset = self.queryset.filter(
                "PtDistWithin(catalogue_origin.position, GeomFromText('%s', "
                "4326), %s)" % (point, distance))
        return self._clone_with_queryset(queryset)

    def group_measures(self, grouping_strategy=None):
        """
        Returns a dictionary where the key identifies an event,
        and the value stores a list of associated measures

        :grouping_strategy: an instance of
           :class:`~eqcatalogue.grouping.GroupMeasuresByHierarchicalClustering`
           or :class:`~eqcatalogue.grouping.GroupMeasuresByEventSourceKey`.
        """

        if not grouping_strategy:
            from eqcatalogue.grouping import GroupMeasuresByEventSourceKey
            grouping_strategy = GroupMeasuresByEventSourceKey()
        return grouping_strategy.group_measures(self)
