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
MatplotLib serializer for Empirical Magnitude Scaling Relationship objects
"""

from matplotlib import pyplot as plt
import numpy as np


def plot(emsr, filename=None, errorbar_params=None,
         line_params=None, figure_params=None):
    """
    Plot an EMSR
    :py:param:: emsr
    An Empirical Magnitude Scaling Relationship object

    :py:param:: filename
    a filename. If None, the plot will be displayed on the screen

    :py:param:: errorbar_params
    a dict object with params passed to matplotlib #errorbar function

    :py:param:: line_params
    a dict object with params passed to matplotlib #plot function

    :py:param:: figure_params
    a dict object with params passed to matplotlib #savefig function
    """

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title("Empirical Magnitude Scaling Relationship between %s and %s" %
                 (emsr.native_measures, emsr.target_measures))

    x = emsr.native_measures.measures
    actual_line_params = {'linestyle': '-', 'lw': 1.5}
    if line_params:
        actual_line_params.update(line_params)

    x_sorted = np.copy(x)
    x_sorted.sort()
    for i, model in enumerate(emsr.regression_models):
        actual_line_params['color'] = str((i * 10) / 255)
        y = model.func(x_sorted)
        ax.plot(x_sorted, y, label=model.long_str(),
                **actual_line_params)

    y = emsr.target_measures.measures
    yerr = emsr.native_measures.sigma * 1.96
    xerr = emsr.native_measures.sigma * 1.96

    actual_errorbar_params = {'fmt': 'b.', 'ecolor': 'r'}
    if errorbar_params:
        actual_errorbar_params.update(errorbar_params)
    plt.errorbar(x, y, xerr=[xerr, xerr], yerr=[yerr, yerr],
                 **actual_errorbar_params)

    plt.xlabel(emsr.native_measures)
    plt.ylabel(emsr.target_measures)
    leg = plt.legend(loc=2, shadow=True, ncol=1)
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize='small')
    plt.ioff()
    actual_figure_params = {}
    if figure_params:
        actual_figure_params.update(figure_params)
    if filename:
        plt.savefig(filename, **actual_figure_params)
    else:
        plt.show()
