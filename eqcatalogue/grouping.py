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
Module :mod:`eqcatalogue.grouping` defines
:class:`GroupMeasuresByEventSourceKey`,
:class:`GroupMeasuresByHierarchicalClustering`,
:class:`GroupMeasuresBySequentialClustering`.
"""

import numpy as np
from collections import defaultdict
from eqcatalogue.models import MagnitudeMeasure
from eqcatalogue import log


# FIXME: Remove the unused import of matplotlib.
# To allow the use of this code on an headless machine we import mpl
# and change the rendering backend to Agg before the module
# scipy.cluster, that is needed in this module and imports matplotlib,
# chooses a rendering backend that requires a display. We remark that
# it is not possible to change the mpl rendering backend once it has
# been set.
import matplotlib
matplotlib.use('Agg')

from scipy.cluster import hierarchy


class GroupMeasuresByEventSourceKey(object):
    """
    Group measures by event source key, that is for each source key of
    an event a group of measure is associated.
    """

    @classmethod
    def group(cls, measures):
        """
        Groups the measures using the event source key as aggregator
        """
        groups = {}
        for m in measures:
            key = m.event_key
            if not key in groups:
                groups[key] = []
            groups[key].append(m)
        log.logger(__name__).info(
            "Measure grouper by source key returned %d groups" % len(groups))
        return groups

    def group_measures(self, measures):
        """
        Groups the measures by event source key
        """
        return self.__class__.group(measures)


class GroupMeasuresByHierarchicalClustering(object):
    """
    Group measures by time clustering using a hierarchical clustering
    algorithm.

    :param key_fn: the function used to get the measure feature we
        perform the clustering on. If not given, a function that
        extract the time of the measure is provided as default.
    :param args: the args passed to scipy.cluster.hierarchy.fclusterdata.
    """

    def __init__(self, key_fn=None, args=None):
        self._clustering_args = {'t': 200, 'criterion': 'distance'}
        if args:
            self._clustering_args.update(args)
        self._key_fn = key_fn or GroupMeasuresByHierarchicalClustering.get_time

    @classmethod
    def get_time(cls, measure):
        """
        return the origin time of the measure, a float with the unix
        timestamp (plus milliseconds)
        """
        return float(measure.time.strftime('%s'))

    def group_measures(self, measures):
        """
        Groups the measures by clustering on time
        """

        data = np.array([self._key_fn(m) for m in measures])
        npdata = np.reshape(np.array(data), [len(data), 1])

        clusters = hierarchy.fclusterdata(npdata, **self._clustering_args)

        grouped = {}
        for i, cluster in enumerate(clusters):
            current = grouped.get(cluster, [])
            current.append(measures[i])
            grouped[cluster] = current

        log.logger(__name__).info(
            "Measure grouper by clustering on time returned %d groups" % len(
                grouped))
        return grouped


class GroupMeasuresBySequentialClustering(object):
    """
        Group measures by sequential clustering, that is first
        measures are grouped in time, then in space and finally in
        magnitude (optional). The user should provide distinct windows
        for time, space and magnitude values.
    """

    def __init__(self, time_window, space_window,
                 time_distance_fn=None, space_distance_fn=None,
                 magnitude_window=None, magnitude_distance_fn=None):
        """
        :param time_window
          The mininum time window in seconds such that two measures are
          in the same group
        :param space_window
          The mininum space window in km such that two measures are
          in the same group
        :param magnitude_window
          The mininum magnitude window in seconds such that two
          measures are in the same group. Be aware that default
          magnitude distance function does not take into account the
          magnitude scale
        :param time_distance_fn
          The function used to compute the time distance (in seconds)
        :param space_distance_fn
          The function used to compute the space distance (in km).
          Default to the Haversine formula
        :param magnitude_distance_fn
          The function used to compute the distance in magnitude between
          two measures
        """
        self.time_window = time_window
        self.space_window = space_window
        self.time_distance_fn = (time_distance_fn or
                                 MagnitudeMeasure.time_distance)
        self.space_distance_fn = (space_distance_fn or
                                  MagnitudeMeasure.space_distance)
        self.magnitude_window = magnitude_window
        self.magnitude_distance_fn = magnitude_distance_fn
        if self.magnitude_window and not self.magnitude_distance_fn:
            self.magnitude_distance_fn = MagnitudeMeasure.magnitude_distance

    def group_measures(self, measures):
        """
        Group `measures` by sequentially applying a grouping on
        time, space and magnitude (optional) variables.
        """

        groups = sum([
            self.group_measures_by_space(time_group)
            for time_group in self.group_measures_by_time(measures)],
            [])

        if self.magnitude_window:
            groups = sum([
                self.group_measures_by_magnitude_value(group)
                for group in groups], [])

        log.logger(__name__).info(
            "Measure grouper (sequential clustering) returned %d groups",
            len(groups))
        return dict([(i, group) for i, group in enumerate(groups)])

    def group_measures_by_time(self, measures):
        """
        Group `measures` in time by using the time_window and the
        time_distance_fn
        """
        groups = self.group_measures_by_var(
            measures, self.time_distance_fn, self.time_window)

        log.logger(__name__).debug(
            "grouping by time returned %d groups", len(groups))
        return groups

    def group_measures_by_magnitude_value(self, measures):
        """
        Group `measures` in magnitude by using the magnitude_window
        and the magnitude_distance_fn. If no magnitude window is
        given, an error is raised
        """
        if not self.magnitude_window:
            raise RuntimeError("Please provide a magnitude window")
        groups = self.group_measures_by_var(
            measures, self.magnitude_distance_fn, self.magnitude_window)

        log.logger(__name__).debug(
            "grouping by magnitude value returned %d groups", len(groups))

        return groups

    def group_measures_by_space(self, measures):
        """
        Group `measures` in space by using the space_window and the
        space_distance_fn
        """
        groups = self.group_measures_by_var(
            measures, self.space_distance_fn, self.space_window)

        log.logger(__name__).debug(
            "grouping by space returned %d groups", len(groups))

        return groups

    def group_measures_by_var(self, measures, distance_fn, window):
        """
        Group measures. Two measures are linked if their distance
        calculated by `distance_fn` is less than `window`. Then, the
        groups are the result of applying recursively the transitive
        property of the link.
        """
        graph = self.__class__.build_graph(
            measures, distance_fn, window)

        return self.__class__.find_connected_components(graph)

    @staticmethod
    def build_graph(measures, fn, threshold):
        """
        Build a graph where the nodes represents measures and two
        nodes n1 and n2 are linked iff fn(n1, n2) < threshold
        """
        return dict([
            (m1,
             [m2
              for m2 in measures
              if m1 != m2 and fn(m1, m2) < threshold])
              for m1 in measures])

    @staticmethod
    def find_connected_components(graph):
        """
        Find the connected components of graph. The algorithm is based
        on multiple BFS search, so it is O(n^3) with n is the number
        of nodes.
        """
        connected_components = defaultdict(lambda: [])

        # find the connected components of graph. We loop through its
        # nodes, starting a new BFS search whenever the loop reaches a
        # node that has not already been included in a previously
        # found connected component.
        for measure in graph.keys():
            if not any([measure in component
                        for component in connected_components.values()]):
                to_visit = [measure]
                visited = {}

                while to_visit:
                    m = to_visit.pop()
                    if not m in connected_components[measure]:
                        connected_components[measure].append(m)
                    visited[m] = True
                    to_visit.extend(
                        [m for m in graph[m] if not visited.get(m)])

        return connected_components.values()
