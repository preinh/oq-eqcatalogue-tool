#!/usr/bin/env python

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


import sys
import os
import argparse

from eqcatalogue import CatalogueDatabase
from eqcatalogue.importers import V1, Iaspei, store_events

fmt_map = {'isf': V1, 'iaspei': Iaspei}


def build_cmd_parser():
    """Create a parser for cmdline arguments"""

    p = argparse.ArgumentParser(prog='LoadCatalogueDB')

    p.add_argument('-i', '--input-file',
                   nargs=1,
                   type=str,
                   metavar='input catalogue file',
                   dest='input_file',
                   help=('Specify the input file containing earthquake'
                         'events supported formats are ISF and IASPEI'))

    p.add_argument('-f', '--format-type',
                   nargs=1,
                   type=str,
                   help=('Specify the earthquake catalogue format,'
                         'valid formats are: isf, iaspei'),
                   metavar='format type',
                   dest='format_type')

    p.add_argument('-d', '--drop-database',
                   action='store_true',
                   help=('Drop the database if present'),
                   dest='drop_database')

    p.add_argument('-db', '--db-name',
                   nargs=1,
                   type=str,
                   default='eqcatalogue.db',
                   help='Specify db filename',
                   metavar='db filename',
                   dest='db_filename')
    return p


def check_args(arguments):
    input_file = arguments.input_file[0]
    fmt_file = arguments.format_type[0]
    fname = (os.path.abspath(input_file)
             if os.path.exists(input_file) else None)
    cat_fmt = (fmt_file.lower()
               if fmt_file.lower() in ['isf', 'iaspei']
               else None)
    if fname is None:
        print 'Can\'t find the provided input file'
        sys.exit(-1)
    if cat_fmt is None:
        print 'Format %s is not supported' % fmt_file
        sys.exit(-1)
    return fname, cat_fmt


if __name__ == '__main__':
    parser = build_cmd_parser()
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        filename, cat_format = check_args(args)
        cat_dbname = (args.db_filename[0] if isinstance(args.db_filename, list)
                      else args.db_filename)
        with open(filename, 'r') as cat_file:
            cat_db = CatalogueDatabase(filename=cat_dbname,
                                       drop=args.drop_database)
            store_events(fmt_map[cat_format], cat_file, cat_db)
        sys.exit(0)
