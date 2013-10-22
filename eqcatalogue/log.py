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
This module contains the definition of the logging facility
"""

import logging
import sys


def setup_logger(log_level=logging.DEBUG,
                 debug_log_filename="eqcatalogue.log"):
    """
    Setup a logger with a FileHandler and a ConsoleHandler for level
    DEBUG and INFO, respectively.

    :param log_level: the default log level of the logger. Default to
    DEBUG

    :param debug_log_filename: the filename used for logging at DEBUG
    level
    """
    root_logger = logging.getLogger('eqcatalogue')

    root_logger.setLevel(log_level)

    fh = logging.FileHandler(debug_log_filename)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    root_logger.addHandler(fh)
    root_logger.addHandler(ch)

    root_logger.debug("Setup logger with level %s and debug filename=%s",
                      log_level, debug_log_filename)

    return root_logger


# for mysterious reasons QGIS may remove .argv from sys, hence the hasattr
if hasattr(sys, 'argv') and sys.argv[0].endswith("nosetests"):
    setup_logger(logging.ERROR)
else:
    setup_logger()


# By using this function, the client is pushed to import this module
# such that the logging is configured properly.
def logger(module_name):
    """
    Returns a logger for `module_name`.
    """
    return logging.getLogger(module_name)
