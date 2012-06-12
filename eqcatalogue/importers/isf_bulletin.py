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


import re
import datetime

from eqcatalogue import models as catalogue

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

    def __init__(self):
        self._catalogue = None

    def setup(self, cat):
        self._catalogue = cat

    def is_start(self):
        return False

    def transition_rule(self, line_type):
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
        return {}


class StartState(BaseState):
    """
    Start State. The FSM is initialized with this state
    """
    def __init__(self):
        super(StartState, self).__init__()
        self.eventsource = None

    def is_start(self):
        return self.eventsource == None

    def _get_next_state(self, line_type):
        if line_type == 'catalogue_header':
            return self
        elif line_type == 'event_header' and self.eventsource:
            return EventState(self.eventsource)

    def process_line(self, line):
        self.eventsource, created = self._save_eventsource(line)
        return {'eventsource_created': 1 if created else 0}

    def _save_eventsource(self, name):
        return self._catalogue.get_or_create(catalogue.EventSource,
                                             {'name': name})


class EventState(BaseState):
    """
    When data about a seismic event arrives, the fsm jumps to an Event
    State
    """
    def __init__(self, eventsource):
        super(EventState, self).__init__()
        self._eventsource = eventsource
        self.event = None

    def _get_next_state(self, line_type):
        if line_type == 'origin_header' and self.event:
            return OriginHeaderState(self.event)

    @classmethod
    def match(cls, line):
        """Return True if line match a proper regexp, that triggers an
        event that makes the fsm jump to an EventState"""
        event_regexp = re.compile(
            '^Event (?P<source_event_id>\w{0,9}) (?P<name>.{0,65})$')
        return event_regexp.match(line)

    def process_line(self, line):
        result = self.__class__.match(line)
        created = self._save_event(**result.groupdict())
        created_nr = 1 if created else 0
        return {'event_created': created_nr}

    def _save_event(self, source_event_id, name):
        self.event, created = self._catalogue.get_or_create(
            catalogue.Event,
            {'source_key': source_event_id,
              'eventsource': self._eventsource})
        if self.event.name != name:
            self.event.name = name
        self._catalogue.session.commit()
        return created


class OriginHeaderState(BaseState):
    def __init__(self, event):
        super(OriginHeaderState, self).__init__()
        self.event = event

    def _get_next_state(self, line_type):
        if line_type == 'origin_block':
            return OriginBlockState(self.event)


class MeasureHeaderState(BaseState):
    def __init__(self, event, metadata):
        super(MeasureHeaderState, self).__init__()
        self.event = event
        self.metadata = metadata

    def _get_next_state(self, line_type):
        if line_type == 'measure_block':
            return MeasureBlockState(self.event, self.metadata)
        elif line_type == 'measure_unknown_scale_block':
            return MeasureUKScaleBlockState(self.event, self.metadata)


class OriginBlockState(BaseState):
    def __init__(self, event):
        super(OriginBlockState, self).__init__()
        self.event = event
        self.agency = None
        self.origin = None
        self.metadata = None

    def _get_next_state(self, line_type):
        if line_type == 'measure_header':
            return MeasureHeaderState(self.event, self.metadata)
        elif line_type == 'origin_block':
            return OriginBlockState(self.event)
        elif line_type == 'event_header':
            return EventState(self.event.eventsource)

    def _process_agency(self, line):
        author = line[118:127].strip()
        self.agency, agency_created = self._save_agency(author)
        return agency_created

    @staticmethod
    def _process_time(line):
        datetime_components = line[0:10].split('/') + \
            line[11:19].split(':')
        # some agency does not provide the msec part
        if line[20:22].strip():
            datetime_components += [line[20:22]]
        datetime_components = [int(d) for d in datetime_components]
        return datetime.datetime(*datetime_components)

    def _process_origin(self, line):
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
            depth_error = float(line[71:76])

        self.origin, origin_created = self._save_origin(
            line[128:136],
            time=time, time_error=time_error, time_rms=time_rms,
            position=position, semi_major_90error=semi_major_90error,
            semi_minor_90error=semi_minor_90error, depth=depth,
            depth_error=depth_error, azimuth_error=azimuth_error)
        return origin_created

    def _process_metadata(self, line):
        strike = None if not line[67:70].strip() else int(line[67:70])
        if line[83:87].strip():
            phases = int(line[83:87])
        else:
            phases = None
        stations_string = line[88:92].strip()

        if stations_string:
            stations = int(stations_string)
        else:
            stations = None

        dist1 = None if not line[97:103].strip() else float(line[97:103])
        dist2 = None if not line[104:110].strip() else float(line[104:110])

        analysis_type_str = line[111].strip()
        if analysis_type_str:
            analysis_type = ANALYSIS_TYPES[analysis_type_str]
        else:
            analysis_type = None
        location_method_str = line[113].strip()
        if location_method_str:
            location_method = LOCATION_METHODS[location_method_str]
        else:
            location_method = None
        event_type = line[115:117].strip()
        event_type = None if not event_type else EVENT_TYPES[event_type]

        self.metadata = {'strike': strike,
                        'phases': phases,
                        'stations': stations,
                        'distance_to_closest_station': dist1,
                        'distance_to_furthest_station': dist2,
                        'analysis_type': analysis_type,
                        'location_method': location_method,
                        'event_type': event_type
                        }

    def process_line(self, line):
        agency_created = self._process_agency(line)
        origin_created = self._process_origin(line)
        self._process_metadata(line)

        return {
            'agency_created': 1 if agency_created else 0,
            'origin_created': 1 if origin_created else 0}

    def _save_agency(self, author):
        return self._catalogue.get_or_create(
            catalogue.Agency,
            {'source_key': author,
             'eventsource': self.event.eventsource})

    def _save_origin(self, source_key, **kwargs):
        return self._catalogue.get_or_create(
            catalogue.Origin,
            {'source_key': source_key,
             'eventsource': self.event.eventsource},
            kwargs)


class MeasureBlockState(BaseState):
    """
    When a Measure Block is found the fsm jumps to this state
    """
    def __init__(self, event, metadata):
        super(MeasureBlockState, self).__init__()
        self.event = event
        self.metadata = metadata

    def _get_next_state(self, line_type):
        if line_type == 'event_header':
            return EventState(self.event.eventsource)
        elif line_type == 'measure_block':
            return MeasureBlockState(self.event, self.metadata)
        elif line_type == 'measure_unknown_scale_block':
            return MeasureUKScaleBlockState(self.event, self.metadata)

    def process_line(self, line):
        scale = line[0:5].strip()
        minmax_indicator = line[5].strip()
        assert(not minmax_indicator)
        value = float(line[6:10])
        if line[11:14].strip():
            standard_magnitude_error = float(line[11:14])
        else:
            standard_magnitude_error = None
        if line[15:19].strip():
            stations = int(line[15:19])
        else:
            stations = None
        agency_name = line[20:29].strip()
        origin_source_key = line[30:38]
        created = self._save_measure(agency_name=agency_name,
                           origin_source_key=origin_source_key,
                           scale=scale,
                           value=value,
                           standard_error=standard_magnitude_error,
            )
        self._save_metadata(stations=stations)
        return {'measure_created': 1 if created else 0}

    def _save_measure(self, agency_name, origin_source_key,
                      scale, value, standard_error):
        agency, _ = self._catalogue.get_or_create(
            catalogue.Agency,
            {'source_key': agency_name,
             'eventsource': self.event.eventsource})
        origin = self._catalogue.session.query(catalogue.Origin).filter_by(
              eventsource=self.event.eventsource,
              source_key=origin_source_key).first()
        self._catalogue.session.commit()
        _, created = self._catalogue.get_or_create(
            catalogue.MagnitudeMeasure,
            {'event': self.event, 'origin': origin,
             'agency': agency, 'scale': scale},
             {'value': value,
              'standard_error': standard_error})
        return created

    def _save_metadata(self, stations):
        self.metadata['stations'] = stations


class MeasureUKScaleBlockState(MeasureBlockState):
    """
    When a Measure Block with an unknown scale is found the fsm jumps
    to this state
    """

    @classmethod
    def match(cls, line):
        pat = ('^(?P<val>-*[0-9]+\.[0-9]+)\s+(?P<error>[0-9]+\.[0-9]+)*\s+'
               '(?P<stations>[0-9]+)*\s+(?P<agency>\w+)\s+(?P<origin>\w+)$')
        return re.compile(pat).match(line)

    def process_line(self, line):
        scale = 'Muk'
        result = MeasureUKScaleBlockState.match(line)
        data = result.groupdict()
        created = self._save_measure(agency_name=data['agency'],
                           origin_source_key=data['origin'],
                           scale=scale,
                           value=data['val'],
                           standard_error=data.get('error'))
        self._save_metadata(stations=data.get('stations'))
        return {'measure_created': 1 if created else 0}


class V1(object):
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
        self._stream = stream
        self._catalogue = cat
        self._summary = {}
        self._state = None
        self._transition(StartState())

    def load(self, allow_junk=True):
        """
        Read and parse from the input stream the data and insert them
        into the catalogue db. If `allow_junk` is True, it allows
        unexpected line inputs at the beginning of the file
        """
        for line in self._stream:
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
                state_output = next_state.process_line(line)
                self._update_summary(state_output)
            except UnexpectedLine as e:
                current = self._state
                if current.is_start() and line_type == 'junk' and allow_junk:
                    continue
                else:
                    raise e
        self._catalogue.session.commit()
        return self._summary

    def _detect_line_type(self, line):
        ORIGIN_FIELDS = ["Date", "Time", "Err", "RMS", "Latitude", "Longitude",
                         "Smaj", "Smin", "Az", "Depth", "Err", "Ndef",
                         "Nst[a]*", "Gap", "mdist", "Mdist", "Qual", "Author",
                         "OrigID"]
        origin_regexp = re.compile('^%s$' % '\s+'.join(ORIGIN_FIELDS))

        MEASURE_FIELDS = ["Magnitude", "Err", "Nsta", "Author", "OrigID"]
        measure_regexp = re.compile('^%s$' % '\s+'.join(MEASURE_FIELDS))

        comment_regexp = re.compile('^\([^\)].+\)')

        if line == 'ISC Bulletin':
            return "catalogue_header"
        elif line == 'STOP':
            return 'stop'
        elif comment_regexp.match(line) or not line.strip():
            return "comment"
        elif origin_regexp.match(line):
            return "origin_header"
        elif measure_regexp.match(line):
            return "measure_header"
        elif EventState.match(line):
            return "event_header"
        elif len(line) == 136 and not self._state.is_start():
            return "origin_block"
        elif len(line) == 38 and not self._state.is_start():
            return "measure_block"
        elif MeasureUKScaleBlockState.match(line):
            return "measure_unknown_scale_block"
        else:
            return "junk"

    def _transition(self, next_state):
        self._state = next_state
        self._state.setup(self._catalogue)

    def _update_summary(self, output):
        for object_type, nr in output.items():
            self._summary[object_type] = self._summary.get(object_type, 0) + nr

    @classmethod
    def import_events(cls, stream, cat):
        """
          Utility that create an instance of the importer and load the
          data from `stream`
        """
        importer = cls(stream, cat)
        return importer.load()
