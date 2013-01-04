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
This module define several functions responsible to output to CSV
format
"""

import csv
from eqcatalogue import log


def export_measures(measures, filename, header=True, mode="w", **kwargs):
    """
    Export `measures` to `filename` by using the csv module from the
    standard python library. If `header` is true the first row of the
    csv will be an header. The remaining arguments of the function are
    passed as they are to the csv writer constructor.
    """
    with open(filename, mode) as csvfile:
        measure_writer = csv.writer(csvfile, **kwargs)

        if header:
            measure_writer.writerow(measures[0].keys())

        for measure in measures:
            measure_writer.writerow(measure.values())

    log.LOG.info("Exported %d measures to %s" % (len(measures), filename))
