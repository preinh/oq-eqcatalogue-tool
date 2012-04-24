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

CSV_FIELDNAMES = ['eventKey', 'solutionKey', 'solutionDesc',
                    'originID', 'year', 'month', 'day', 'hour',
                    'minute', 'second', 'timeError', 'time_rms',
                    'Latitude', 'Longitude', 'semiMajor90',
                    'semiMinor90', 'errorAzimuth', 'depth',
                    'depthError', 'phases', 'stations', 'azimuthGap',
                    'minDistance', 'maxDistance', 'solutionID',
                    'magnitude', 'magnitudeError', 'magStations',
                    'solutionAgency', 'mag_type', 'mag_agency']


def convert_to_int(str_value):
    value = None
    try:
        value = int(str_value)
    except ValueError:
        pass
    return value


def convert_to_float(str_value):
    value = None
    try:
        value = float(str_value)
    except ValueError:
        pass
    return value


STR_TRANSF = [str.strip]
INT_TRANSF = [convert_to_int]
FLOAT_TRANSF = [convert_to_float]

TRANSF_MAP = {'eventKey': INT_TRANSF, 'solutionKey': INT_TRANSF,
                'solutionDesc': STR_TRANSF, 'originID': INT_TRANSF,
                'year': INT_TRANSF, 'month': INT_TRANSF, 'day': INT_TRANSF,
                'hour': INT_TRANSF, 'minute': INT_TRANSF,
                'second': FLOAT_TRANSF, 'timeError': FLOAT_TRANSF,
                'time_rms': FLOAT_TRANSF, 'Latitude': FLOAT_TRANSF,
                'Longitude': FLOAT_TRANSF, 'semiMajor90': FLOAT_TRANSF,
                'semiMinor90': FLOAT_TRANSF, 'errorAzimuth': FLOAT_TRANSF,
                'depth': FLOAT_TRANSF, 'depthError': FLOAT_TRANSF,
                'phases': INT_TRANSF, 'stations': INT_TRANSF,
                'azimuthGap': FLOAT_TRANSF, 'minDistance': FLOAT_TRANSF,
                'maxDistance': FLOAT_TRANSF, 'solutionID': INT_TRANSF,
                'magnitude': FLOAT_TRANSF, 'solutionAgency': STR_TRANSF,
                'mag_type': STR_TRANSF, 'mag_agency': STR_TRANSF,
                'magnitudeError': FLOAT_TRANSF, 'magStations': INT_TRANSF}
