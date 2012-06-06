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
Exception module for the eqcatalogue tool
"""


class RegressionFailedException(BaseException):
    def __init__(self, reason):
        super(RegressionFailedException, self).__init__(self)
        self.reason = reason

    def __repr__(self):
        return "Regression failed: %s" % self.reason


class NotEnoughSamples(BaseException):
    def __repr__(self):
        return """
        Not enough measures to perform regression.
        Please relax your query or selection criteria"""
