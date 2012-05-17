"""
Model Managers definition
"""

import eqcatalogue.models as db


class MeasureManager(object):
    """
    Manage a list of quantitative measures
    :py:attribute:: measures
    A list of float
    :py:attribute:: sigma
    Standard error of measures. Can be fixed (a single float) or a
    list of float
    :py:attribute:: name
    the magnitude scale
    """
    def __init__(self, name):
        self.measures = []
        self.sigma = []
        self.name = name
        # holds a list of magnitude measure objects
        self.magnitude_measures = []

    def append(self, measure):
        self.magnitude_measures.append(measure)
        self.measures.append(measure.value)

    def __repr__(self):
        return self.name

    def __iter__(self):
        return self.measures.__iter__()

    def __len__(self):
        return len(self.measures)


class EventManager(object):
    """
    Manage a list of event.
    :param cat: a Catalogue Database object
    :param queryset: the base queryset of events (defaults to all
    events), the eventmanager works on
    """

    def __init__(self, cat=None, queryset=None):
        self.cat = cat or db.CatalogueDatabase()
        self._session = self.cat.session
        self.queryset = self._session.query(db.Event).join(
            db.MagnitudeMeasure).join(db.Origin).join(db.Agency)
        if queryset:
            self.queryset = self.queryset.filter(
                db.Event.id.in_([e.id for e in queryset.all()]))

    @classmethod
    def clone_with_queryset(self, em, queryset):
        """Create another EventManager with the same catalogue and
        initializing queryset with the passed one"""
        new_em = EventManager(em.cat, queryset)
        return new_em

    def all(self):
        """Layer compat with SQLAlchemy Query object"""
        return self.queryset.all()

    def count(self):
        """Layer compat with SQLAlchemy Query object"""
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

    def group_measures(self):
        """
        Group all measures by event
        :param query_obj: sqlalchemy query object.
        """

        groups = []
        for ev in self.queryset.all():
            groups.append(dict(event=ev, measures=ev.measures))
        return groups
