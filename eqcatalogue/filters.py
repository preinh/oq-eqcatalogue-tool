"""
Model Managers definition
"""

import eqcatalogue.models as db
import numpy as np

# we import matplotlib just to change the backend as scipy import
# matplotlib making impossible to use this code on an headless machine
import matplotlib
matplotlib.use('Agg')
from scipy.cluster import hierarchy


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
            grouping_strategy = GroupMeasuresByEventSourceKey()
        return grouping_strategy.group_measures(self)


class GroupMeasuresByEventSourceKey(object):
    """
    Group measures by event source key, that is for each source key of
    an event a group of measure is associated
    """
    def group_measures(self, event_manager):
        groups = {}
        for ev in event_manager.all():
            groups[str(ev.source_key)] = ev.measures
        return groups


class GroupMeasuresByHierarchicalClustering(object):
    """
    Group measures by time clustering using a hierarchical clustering
    algorithm
    """
    def __init__(self, key_fn=None, args=None):
        """
        Initialize an instance.
        :py:param:: key_fn
        the function used to get the measure feature we perform the
        clustering on. If not given, a function that extract the
        time of the measure is provided as default
        :py:param:: args
        the args passed to scipy.cluster.hierarchy.fclusterdata
        """
        self._clustering_args = {'t': 200,
            'criterion': 'distance'
            }
        if args:
            self._clustering_args.update(args)
        self._key_fn = key_fn or GroupMeasuresByHierarchicalClustering.get_time

    @classmethod
    def get_time(cls, measure):
        return float(measure.origin.time.strftime('%s'))

    def group_measures(self, event_manager):
        cat = db.CatalogueDatabase()
        event_ids = [e.id for e in event_manager.all()]

        # get the measures related with the event manager
        measures = cat.session.query(db.MagnitudeMeasure).filter(
            db.MagnitudeMeasure.event_id.in_(event_ids)).all()

        data = np.array([self._key_fn(m) for m in measures])
        npdata = np.reshape(np.array(data), [len(data), 1])

        # cluster them
        clusters = hierarchy.fclusterdata(npdata, **self._clustering_args)

        grouped = {}
        for i, cluster in enumerate(clusters):
            current = grouped.get(cluster, [])
            current.append(measures[i])
            grouped[cluster] = current
        return grouped
