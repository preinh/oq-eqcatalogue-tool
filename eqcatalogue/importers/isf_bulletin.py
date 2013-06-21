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
This module define an Importer class used to import seismic data
events from catalogue saved in the ISF Format
http://www.isc.ac.uk/standards/isf/
"""

import re
import datetime
from sqlalchemy.exc import IntegrityError

from eqcatalogue import models as catalogue

from eqcatalogue.log import logger
from eqcatalogue.importers import BaseImporter
from eqcatalogue.exceptions import ParsingFailure


LOG = logger(__name__)
CATALOG_URL = 'http://www.isc.ac.uk/cgi-bin/web-db-v4'

ANALYSIS_TYPES = {'a': 'automatic',
                  'm': 'manual',
                  'g': 'guess'}

LOCATION_METHODS = {
    'i': 'inversion',
    'p': 'pattern recognition',
    'g': 'ground truth',
    'o': 'other'
}

EVENT_TYPES = {
    'uk': 'unknown',
    'de': 'damaging earthquake ( Not standard IMS )',
    'fe': 'felt earthquake ( Not standard IMS )',
    'ke': 'known earthquake',
    'se': 'suspected earthquake',
    'kr': 'known rockburst',
    'sr': 'suspected rockburst',
    'ki': 'known induced event',
    'si': 'suspected induced event',
    'km': 'known mine expl.',
    'sm': 'suspected mine expl.',
    'kh': 'known chemical expl. ( Not standard IMS )',
    'sh': 'suspected chemical expl. ( Not standard IMS )',
    'kx': 'known experimental expl.',
    'sx': 'suspected experimental expl.',
    'kn': 'known nuclear expl.',
    'sn': 'suspected nuclear explosion',
    'ls': 'landslide'
}


UNKNOWN_EVENT_TYPE_DESCRIPTION = "unknown event type"

ERR_MSG = ('The line %s violates the format, please check the related format'
           ' documentation at: http://www.isc.ac.uk/standards/isf/')


class UnexpectedLine(BaseException):
    """
    Exception raised when an unexpected line input is found
    """
    pass

# Imp. Notes. Parsing is done by using a FSM. Each line has a
# line_type which acts as an "event" and it is an instance of a
# particular State


class BaseState(object):
    """
    The base state object. A state stores the catalogue db instance
    and calculate the next state based on the current event
    """

    def __init__(self, context=None):
        self._catalogue = None
        self.context = context

    def setup(self, cat):
        """
        Save the catalogue `cat` to allow further data insert
        operation
        """
        self._catalogue = cat

    def is_start(self):
        """
        Return true if the state can be a starting state
        """
        return False

    def _get_next_state(self, line_type):
        """
        Given the next detected `line_type` returns the next state or
        None if no next_state could be derived
        """
        raise NotImplementedError

    def transition_rule(self, line_type):
        """
        Given the next detected `line_type` returns the next state or
        raise UnexpectedLine error if no next_state could be derived
        """
        next_state = self._get_next_state(line_type)
        if not next_state:
            raise UnexpectedLine(
                "Invalid Line Type Exception in state %s \
                found line_type %s" % (self, line_type))
        else:
            return next_state

    def process_line(self, _):
        """
        When a state is initialized, this function is called. It
        actually parses the line content and eventually creates the
        proper model object. It returns a dictionary with the partial
        summary of this import phase
        """
        pass


class StartState(BaseState):
    """
    Start State. The FSM is initialized with this state
    """
    def __init__(self):
        super(StartState, self).__init__()
        self.started = None

    def is_start(self):
        return self.started is None

    def _get_next_state(self, line_type):
        if line_type == 'catalogue_header':
            return self
        elif line_type == 'event_header' and self.started:
            return EventState(self.context)

    def process_line(self, line):
        self.context['current_event_source'] = line
        self.started = True


class EventState(BaseState):
    """
    When data about a seismic event arrives, the fsm jumps to an Event
    State
    """
    def _get_next_state(self, line_type):
        if (line_type == 'origin_header' and
            'current_event' in self.context):
            return OriginHeaderState(self.context)

    @classmethod
    def match(cls, line):
        """Return True if line match a proper regexp, that triggers an
        event that makes the fsm jump to an EventState"""
        event_regexp = re.compile(
            r'^Event\s+(?P<source_event_id>\w{0,9}) (?P<name>.{0,65})$')
        return event_regexp.match(line)

    def process_line(self, line):
        result = self.__class__.match(line).groupdict()
        source_event_id, name = result['source_event_id'], result['name']
        self.context['current_event'] = (source_event_id, name)


class OriginHeaderState(BaseState):
    """
    Parse the Header of an Origin block. An Origin block holds the
    information about the origins and the agencies related to the
    current parsed event.
    """
    def _get_next_state(self, line_type):
        if line_type == 'origin_block':
            return OriginBlockState(self.context)


class MeasureHeaderState(BaseState):
    """
    Parse the Header of a Measure Block.
    """
    def _get_next_state(self, line_type):
        if line_type == 'measure_block':
            return MeasureBlockState(self.context)
        elif line_type == 'measure_unknown_scale_block':
            return MeasureUKScaleBlockState(self.context)


class OriginBlockState(BaseState):
    """
    Parse the Origin Block
    """
    def _get_next_state(self, line_type):
        if line_type == 'measure_header':
            return MeasureHeaderState(self.context)
        elif line_type == 'origin_block':
            return OriginBlockState(self.context)
        elif line_type == 'event_header':
            return EventState(self.context)

    @staticmethod
    def _process_time(line):
        """
        Extract and return the time expected in UTC
        """
        datetime_components = line[0:10].split('/') + \
            line[11:19].split(':')
        # some agency does not provide the msec part
        if line[20:22].strip():
            datetime_components += [line[20:22]]
        datetime_components = [int(d) for d in datetime_components]
        return datetime.datetime(*datetime_components)

    def process_line(self, line):
        """
        Extract the origin data, save and return the current parsed
        origin
        """
        time = OriginBlockState._process_time(line)

        if line[22] == 'f':
            time_error = None
        else:
            if line[24:29].strip():
                time_error = float(line[24:29])
            else:
                time_error = None
        time_rms = None if not line[30:35].strip() else float(line[30:35])

        position = self._catalogue.position_from_latlng(float(line[36:44]),
                                                        float(line[45:54]))
        position = "GeomFromText('POINT(%s %s)', 4326)" % (
            float(line[45:54]), float(line[36:44]))
        fixed_position = line[54] == 'f'
        errors = (line[55:60].strip(), line[61:66].strip())
        if fixed_position or not errors[0]:
            semi_major_90error = None
        else:
            semi_major_90error = float(errors[0])

        if fixed_position or not errors[1]:
            semi_minor_90error = None
        else:
            semi_minor_90error = float(errors[1])

        azimuth_error = None if not line[93:96].strip() else int(line[93:96])

        if line[71:76].strip():
            depth = float(line[71:76])
        else:
            depth = None
        if line[76] == 'f' or not line[78:82].strip():
            depth_error = None
        else:
            depth_error = float(line[78:82])

        self.context['origins'][line[128:136].strip()] = dict(
            time=time, time_error=time_error, time_rms=time_rms,
            position=position, semi_major_90error=semi_major_90error,
            semi_minor_90error=semi_minor_90error, depth=depth,
            depth_error=depth_error, azimuth_error=azimuth_error)


class MeasureBlockState(BaseState):
    """
    When a Measure Block is found the fsm jumps to this state
    """
    def _get_next_state(self, line_type):
        if line_type == 'event_header':
            return EventState(self.context)
        elif line_type == 'measure_block':
            return MeasureBlockState(self.context)
        elif line_type == 'measure_unknown_scale_block':
            return MeasureUKScaleBlockState(self.context)

    def process_line(self, line):
        scale = line[0:5].strip()

        # at the moment we do not support min/max indicator
        minmax_indicator = line[5].strip()
        assert(not minmax_indicator)

        value = float(line[6:11])
        if line[11:14].strip():
            standard_error = float(line[11:14])
        else:
            standard_error = None
        agency_name = line[19:29].strip()
        origin_source_key = line[30:38].strip()
        self._save_measure(
            agency_name, scale, value, standard_error, origin_source_key)

    def _save_measure(self,
                      agency_name, scale, value, standard_error,
                      origin_source_key):
        params = dict(event_source=self.context['current_event_source'],
                      event_key=self.context['current_event'][0],
                      event_name=self.context['current_event'][1],
                      agency=agency_name,
                      scale=scale,
                      value=value,
                      standard_error=standard_error,
                      origin_key=origin_source_key)
        params.update(self.context['origins'][origin_source_key])

        self._catalogue.session.execute("""
INSERT OR REPLACE INTO catalogue_magnitudemeasure(
created_at, scale, value, standard_error, event_source,
event_key, event_name, agency, origin_key, time, time_error, time_rms,
semi_major_90error, semi_minor_90error, position, depth, depth_error,
azimuth_error)
VALUES(datetime(), :scale, :value, :standard_error, :event_source,
:event_key, :event_name, :agency, :origin_key, :time, :time_error, :time_rms,
:semi_major_90error, :semi_minor_90error, %s,
:depth, :depth_error, :azimuth_error)""" % params['position'], params)


class MeasureUKScaleBlockState(MeasureBlockState):
    """
    When a Measure Block with an unknown scale is found the fsm jumps
    to this state
    """

    @classmethod
    def match(cls, line):
        """
        Use a regular expression to parse measure block with an
        unknown scale. Returns true if the line matches the pattern
        """
        pat = (r'^(?P<val>-*[0-9]+\.[0-9]+)\s+(?P<error>[0-9]+\.[0-9]+)*\s+'
               r'(?P<stations>[0-9]+)*\s+(?P<agency>[\w;]+)'
               r'\s+(?P<origin>\w+)$')
        return re.compile(pat).match(line)

    def process_line(self, line):
        scale = 'Muk'
        result = MeasureUKScaleBlockState.match(line)
        data = result.groupdict()
        self._save_measure(
            agency_name=data['agency'],
            origin_source_key=data['origin'],
            scale=scale,
            value=data['val'],
            standard_error=data.get('error'))


class Importer(BaseImporter):
    """
    Import data into a CatalogueDatabase from stream objects.

    The specification of the format can be found at
    http://www.isc.ac.uk/standards/isf/

    Data file in ISF format can be generated at
    http://www.isc.ac.uk/iscbulletin/search/bulletin/

    by flagging "Only prime hypocentre" and checking that "Output web
    links" is unchecked
    """

    def __init__(self, stream, cat):
        """
        Initialize the importer.

        :param: stream:
          A stream object storing the seismic event data
        :type stream: file

        :param: cat:
          The catalogue database used to import the data
        :type cat: CatalogueDatabase
        """
        super(self.__class__, self).__init__(stream, cat)
        # we save the initial state, because it also acts like a
        # rollback state
        self._initial = StartState()
        self._state = None
        self._transition(self._initial)

    def store(self, allow_junk=True, on_line_read=None):
        """
        Read and parse from the input stream the data and insert them
        into the catalogue db. If `allow_junk` is True, it allows
        unexpected line inputs at the beginning of the file
        """
        for line_num, line in enumerate(self._file_stream, start=1):
            if on_line_read is not None:
                on_line_read(self, line_num)
            line = line.strip()

            # line_type acts as "event" in the traditional fsm jargon.
            # Here we use line_type do not confuse with seismic event
            line_type = self._detect_line_type(line)

            # skip comments and exit condition
            if line_type == "comment":
                continue
            elif line_type == "stop":
                break

            try:
                next_state = self._state.transition_rule(line_type)
                self._transition(next_state)
                next_state.process_line(line)
                if line_num % 250000 == 0:
                    LOG.info('%dk lines processed' % (line_num / 1000))
                    self._catalogue.session.commit()
            except IntegrityError:
                # we can not skip an integrity error
                LOG.warn('Measure already present. linenum %d' % line_num)
                raise self._parsing_error(line_num)
            except (UnexpectedLine, ValueError):
                current = self._state
                if current.is_start() and line_type == 'junk' and allow_junk:
                    continue
                else:
                    LOG.warn('Unexpected line at linenum %d' % line_num)
                    self.errors.append(self._parsing_error(line_num))
                    self._state = self._initial
        self._catalogue.session.commit()

    def _parsing_error(self, line_num):
        """
        Issue a rollback and return a parsing error exception
        """
        self._catalogue.session.rollback()
        return ParsingFailure(ERR_MSG % line_num)

    def _detect_line_type(self, line):
        """
        Given the current `line` detect and returns its line_type
        """
        origin_fields = ["Date", "Time", "Err", "RMS", "Latitude", "Longitude",
                         "Smaj", "Smin", "Az", "Depth", "Err", "Ndef",
                         "Nst[a]*", "Gap", "mdist", "Mdist", "Qual", "Author",
                         "OrigID"]
        origin_regexp = re.compile('^%s$' % r'\s+'.join(origin_fields))

        measure_fields = ["Magnitude", "Err", "Nsta", "Author", "OrigID"]
        measure_regexp = re.compile('^%s$' % r'\s+'.join(measure_fields))

        comment_regexp = re.compile(r'^\([^\)].+\)')

        if line == 'ISC Bulletin':
            line_type = "catalogue_header"
        elif line == 'STOP':
            line_type = 'stop'
        elif comment_regexp.match(line) or not line.strip():
            line_type = "comment"
        elif origin_regexp.match(line):
            line_type = "origin_header"
        elif measure_regexp.match(line):
            line_type = "measure_header"
        elif EventState.match(line):
            line_type = "event_header"
        elif len(line) == 136 and not self._state.is_start():
            line_type = "origin_block"
        elif len(line) == 38 and not self._state.is_start():
            line_type = "measure_block"
        elif MeasureUKScaleBlockState.match(line):
            line_type = "measure_unknown_scale_block"
        else:
            line_type = "junk"

        return line_type

    def _transition(self, next_state):
        """
        Perform the transition to `next_state` by saving it and
        initializing the new state
        """
        self._state = next_state
        if self._state.context is None:
            self._state.context = dict(origins={},
                                       current_event=None,
                                       current_event_source=None)
        self._state.setup(self._catalogue)
