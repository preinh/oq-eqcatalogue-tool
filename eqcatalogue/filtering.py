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
Module :mod:`eqcatalogue.filtering` defines the abstract class
:class:`Criteria` and its derived classes.
"""

import eqcatalogue.models as db
from eqcatalogue import exceptions
from eqcatalogue import serializers


class Criteria(object):
    """
    Allows to describe criteria on measures. Criteria can be used to
    check if a criteria holds for a measure and to return all the
    measures stored in a catalogue database that statisfy the
    specified criteria. Criteria can be combined with logical
    operators.

    :param _cat: a Catalogue Database object.
    """

    def __init__(self):
        self._cat = db.CatalogueDatabase()
        self._session = self._cat.session
        self.default_queryset = self._session.query(
            db.MagnitudeMeasure).join(db.Origin).join(db.Agency)

    def filter(self, queryset=None):
        """
        Returns all the measures that satistify the criteria from a
        given set of measures. If `queryset` is empty all the measures
        in the catalogue are considered
        """
        queryset = queryset or self.default_queryset
        return queryset

    def all(self, order_field='catalogue_magnitudemeasure.id'):
        """
        Returns all the measures that satisfies the criteria in a list
        ordered by `order_field`.
        """
        return self.filter().order_by(order_field).all()

    def __iter__(self):
        """
        Returns an iterator on all the measures that fulf
        """
        return self.filter().__iter__()

    def __len__(self):
        return self.count()

    def __contains__(self, el):
        return self.predicate(el)

    def events(self):
        """
        Returns all the distinct events associated with all the
        measures that satisfies the criteria
        """

        subquery = self.filter().subquery()
        return self._session.query(db.Event).join(subquery).all()

    def count(self):
        """
        Returns a count of all the measures that satisfies the criteria.
        """

        return self.filter().count()

    def predicate(self, measure):
        """
        Returns true if the criteria fulfills for the specified
        `measure`. It should be implemented by derived classes,
        otherwise a query is performed for check the existance
        """
        return measure in self.filter()

    def __and__(self, criteria):
        """
        Combines the criteria with another `criteria` by logical and
        """
        return CombinedCriteria(self, criteria)

    def __getitem__(self, item):
        """
        Support for the index protocol
        """
        return self.all()[item]

    def __or__(self, criteria):
        """
        Combines the criteria with another `criteria` by logical or
        """
        return AlternativeCriteria(self, criteria)

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

    def export(self, fmt, **fmt_args):
        """
        Export the measures that satisfies to this criteria in the
        format `fmt`. All the remaining arguments are passed to the
        exporter. E.g.

        C().export('csv', filename="test.csv")
        """
        serializers.get_measure_exporter(fmt)(self.all(), **fmt_args)


class CombinedCriteria(Criteria):
    """
    A criteria that is the and-combination of two criterias
    """
    def __init__(self, criteria1, criteria2):
        super(CombinedCriteria, self).__init__()
        self.criteria1 = criteria1
        self.criteria2 = criteria2

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return self.criteria1.filter(self.criteria2.filter(queryset))

    def predicate(self, measure):
        return (self.criteria1.predicate(measure) and
                self.criteria2.predicate(measure))

    def __repr__(self):
        return "(%s AND %s)" % (self.criteria1, self.criteria2)


class AlternativeCriteria(Criteria):
    """
    A criteria that is the or-combination of two criterias
    """
    def __init__(self, criteria1, criteria2):
        super(AlternativeCriteria, self).__init__()
        self.criteria1 = criteria1
        self.criteria2 = criteria2

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return (self.criteria1.filter(queryset).union(
                self.criteria2.filter(queryset)))

    def predicate(self, measure):
        return (self.criteria1.predicate(measure) or
                self.criteria2.predicate(measure))

    def __repr__(self):
        return "(%s OR %s)" % (self.criteria1, self.criteria2)


class Before(Criteria):
    """
    all the measures before a specified time

    :attrib time: datetime object.
    """

    def __init__(self, time):
        super(Before, self).__init__()
        self.time = time

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return queryset.filter(db.Origin.time < self.time)

    def predicate(self, measure):
        return measure.origin.time < self.time

    def __repr__(self):
        return "<before %s>" % self.time


class After(Criteria):
    """
    all the measures after a specified time.

    :attribute time: datetime object.
    """

    def __init__(self, time):
        super(After, self).__init__()
        self.time = time

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return queryset.filter(db.Origin.time > self.time)

    def predicate(self, measure):
        return measure.origin.time > self.time

    def __repr__(self):
        return "<after %s>" % self.time


class Between(Criteria):
    """
    all the measures within a time range

    :attribute time_lb: time range lower bound.
    :attribute time_ub: time range upper bound.
    """
    def __init__(self, bounds):
        super(Between, self).__init__()
        self.time_lb, self.time_ub = bounds
        self._comb = Before(self.time_ub) & After(self.time_lb)

    def filter(self, queryset=None):
        return self._comb.filter(queryset)

    def predicate(self, measure):
        return self._comb.predicate(measure)

    def __repr__(self):
        return repr(self._comb)


class WithAgencies(Criteria):
    """
    all the measures which have one of the defined agencies

    :attribute agency_name_list: a list of agency names
    """

    def __init__(self, agency_name_list):
        super(WithAgencies, self).__init__()
        self.agencies = agency_name_list

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return queryset.filter(
            db.Agency.source_key.in_(self.agencies))

    def predicate(self, measure):
        return measure.agency.source_key in self.agencies

    @classmethod
    def make_with_agency(cls, agency):
        return cls([agency])

    def __repr__(self):
        return "<agencies in %s>" % self.agencies


class WithMagnitudeScales(Criteria):
    """
    all the measures which have one of the specified magnitude
    scales

    :attribute scales: a list of magnitude scales.
    """
    def __init__(self, scales):
        super(WithMagnitudeScales, self).__init__()
        self.scales = scales

    @classmethod
    def make_with_scale(cls, scale):
        return cls([scale])

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return queryset.filter(
            db.MagnitudeMeasure.scale.in_(self.scales))

    def predicate(self, measure):
        return measure.scale in self.scales

    def __repr__(self):
        return "<scale in %s>" % self.scales


class WithMagnitudeGreater(Criteria):
    """
    all the measures which have one of the specified magnitude
    value bigger than a value

    :attribute value: the value considered
    """
    def __init__(self, value):
        super(WithMagnitudeGreater, self).__init__()
        self.value = value

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return queryset.filter(db.MagnitudeMeasure.value > self.value)

    def predicate(self, measure):
        return measure.value > self.value

    def __repr__(self):
        return "<magnitude > %s>" % self.value


class WithinPolygon(Criteria):
    """
    all the measures within a specified polygon

    :attribute polygon: a polygon specified in wkt format.
    """

    def __init__(self, polygon):
        super(WithinPolygon, self).__init__()
        self.polygon = polygon

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return queryset.filter(
            db.Origin.position.within(self.polygon))

    def __repr__(self):
        return "<within %s>" % self.polygon


class WithinDistanceFromPoint(Criteria):
    """
    all measures within a specified distance from a point.

    :attribute point: a point specified in wkt format.
    :attribute distance: distance specified in meters (see srid 4326).
    """

    def __init__(self, params):
        self.point, self.distance = params
        super(WithinDistanceFromPoint, self).__init__()

    def filter(self, queryset=None):
        queryset = queryset or self.default_queryset
        return queryset.filter(
            "PtDistWithin(catalogue_origin.position, GeomFromText('%s', "
            "4326), %s)" % (self.point, self.distance))

    def __repr__(self):
        return "<within distance %s from %s>" % (self.distance, self.point)


CRITERIA_MAP = {
    'before': Before,
    'after': After,
    'between': Between,
    'agency__in': WithAgencies,
    'agency': WithAgencies.make_with_agency,
    'scale__in': WithMagnitudeScales,
    'scale': WithMagnitudeScales.make_with_scale,
    'within_polygon': WithinPolygon,
    'within_distance_from_point': WithinDistanceFromPoint,
    'magnitude__gt': WithMagnitudeGreater
}

CRITERIA_AVAILABLES = CRITERIA_MAP.keys()


def C(**criteria_kwargs):
    """
    A factory of criterias.
    Example: C(scale="Mw") & C(magnitude__gt=5, agency="ISC")
    """
    criteria = None

    for criteria_arg, criteria_value in criteria_kwargs.items():

        criteria_class = CRITERIA_MAP.get(criteria_arg)

        if not criteria_class:
            raise exceptions.InvalidCriteria(
                """%s does not indicate any known filter.
        Valid criteria keywords includes: %s""" % (
            criteria_arg, "\n".join(CRITERIA_AVAILABLES)))

        current_criteria = criteria_class(criteria_value)

        if criteria is None:
            criteria = current_criteria
        else:
            criteria = criteria & current_criteria

    if criteria is None:
        return Criteria()
    else:
        return criteria
