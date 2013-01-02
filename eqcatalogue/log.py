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
    logger = logging.getLogger('eqcatalogue')

    logger.setLevel(log_level)

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
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.debug("Setup logger with level %s and debug filename=%s",
                 log_level, debug_log_filename)

    return logger


if sys.argv[0].endswith("nosetests"):
    LOG = setup_logger(logging.ERROR)
else:
    LOG = setup_logger()
