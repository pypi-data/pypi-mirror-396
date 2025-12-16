#cython: language_level=3

import array
import ctypes
import logging
from logging.handlers import SysLogHandler
import importlib
import importlib.util
from multiprocessing import Process, SimpleQueue, shared_memory
import multiprocessing as mp
import numbers
import os
from pathlib import Path
import pickle
import platform
import struct
import subprocess
import sys
import time
import warnings

from libc.stdio cimport snprintf
from libc.stdlib cimport calloc, free, malloc
from libc.string cimport strcpy, memcpy, strncpy, memset
from cpython cimport array
cimport cython
import numpy as np
cimport numpy as np

from pippi import dsp, midi, ugens
from pippi.soundbuffer cimport SoundBuffer
from pippi.ugens cimport (
    Graph, 
    LPUgen, 
    ugen_t, 
    UgenTypes, 
    UgenParams, 
    UGEN_SINE, 
    UGEN_TAPE, 
    UGEN_ADC, 
    UGEN_MULT, 
    UGEN_PULSAR
)

NUM_COMRADES = 30

cdef dict DEFAULT_PARAMS = {
    'volume': 'float',
}

class InstrumentError(Exception):
    pass

logger = logging.getLogger('astrid-cyrenderer')
if not logger.handlers:
    if platform.system() == 'Darwin':
        log_path = '/var/run/syslog'
    else:
        log_path = '/dev/log'

    logger.addHandler(SysLogHandler(address=log_path))
    logger.setLevel(logging.DEBUG)
    warnings.simplefilter('always')


cdef class MessageEvent:
    def __cinit__(self,
            Renderer r,
            double onset,
            str instrument_name=None,
            int msgtype=-1,
            str params=None,
            double max_processing_time=0,
            int voice_id=0,
            str cmd=None, 
            *args, **kwargs
        ):
        cdef size_t onset_frames = 0
        cdef char * _cmd
        cdef char * byte_params
        cdef char * byte_instrument_name 
        cdef int channel, velocity, device_index, note, midi_message_type

        self.msg.initiated = 0
        self.msg.scheduled = onset
        self.msg.max_processing_time = max_processing_time
        self.msg.onset_delay = 0
        self.msg.voice_id = voice_id
        self.msg.count = 0
        self.msg.type = msgtype
        self.msg.flags = LPFLAG_IS_SCHEDULED if onset > 0 else LPFLAG_NONE
        self.r = r

        if msgtype == LPMSG_MIDI_TO_DEVICE:
            channel = kwargs.get('channel', 0)
            note = kwargs.get('note', 60)
            velocity = kwargs.get('velocity', 127)
            midi_message_type = kwargs.get('message_type', NOTE_ON)
            device_index = kwargs.get('device_index', 0)
            self.msg.voice_id = device_index
            lpmidi_encode_msg(&self.msg, channel, midi_message_type, note, velocity)
            return

        if msgtype == LPMSG_GRAPH_UPDATE_READY:
            graph = kwargs.get('graph', None)
            if graph is None:
                raise ValueError('Missing graph for update')
            cmd = str(graph)
            cmd_byte_string = cmd.encode('utf-8')
            _cmd = cmd_byte_string
            memcpy(self.msg.msg, _cmd, len(cmd))

            if instrument_name is not None:
                instrument_name_byte_string = instrument_name.encode('utf-8')
                byte_instrument_name = instrument_name_byte_string
                strcpy(self.msg.instrument_name, byte_instrument_name)
            return

        if cmd is not None:
            cmd_byte_string = cmd.encode('utf-8')
            _cmd = cmd_byte_string
            parse_message_from_external_cmdline(_cmd, &self.msg)

        else:
            params_byte_string = params.encode('utf-8')
            instrument_name_byte_string = instrument_name.encode('utf-8')
            byte_params = params_byte_string
            byte_instrument_name = instrument_name_byte_string
            strcpy(self.msg.msg, byte_params)
            strcpy(self.msg.instrument_name, byte_instrument_name)

    cpdef int schedule(MessageEvent self, size_t now=0):
        self.msg.initiated = now
        # internal messages are sent via the internal ringbuffer
        if lphashstr(self.msg.instrument_name) == self.r.name_hash:
            return self.r.write_to_internal_queue(&self.msg)
        # messages to external instruments (and eventually network targets?)
        # are sent to the other instrument's POSIX message inbox
        logger.warning('external communication not supported')


cdef class EventTriggerFactory:
    def __cinit__(self, Renderer r):
        self.r = r

    def _parse_params(self, *args, **kwargs):
        params = ' '.join(map(str, args)) 
        params += ' ' 
        params += ' '.join([ '%s=%s' % (k, v) for k, v in kwargs.items() ])

        logger.debug('_parse_params params=%s' % params)

        return params

    cpdef midinote(self, double onset, str instrument_name, double length, double freq=0, double amp=-1, int note=60, int velocity=127, int channel=1, int device_index=0):
        cdef char _note, _velocity
        cdef MessageEvent noteon
        cdef MessageEvent noteoff
       
        if freq > 0:
            _note = <char>midi.ftomi(freq)
        else:
            _note = <char>max(0, min(127, note))

        if amp >= 0:
            _velocity = <char>max(0, min(127, (amp * 127)))
        else:
            _velocity = <char>max(0, min(127, velocity))

        noteon = MessageEvent(self.r, onset, instrument_name, message_type=NOTE_ON, note=_note, velocity=_velocity, channel=channel, device_index=device_index)
        noteoff = MessageEvent(self.r, onset + length, instrument_name, message_type=NOTE_OFF, note=_note, velocity=_velocity, channel=channel, device_index=device_index)

        return [noteon, noteoff]

    cpdef midi(self, double onset, str instrument_name, int b1, int b2, int b3, int device_index=0):
        cdef int event_type = NOTE_ON
        cdef int channel = 0

        return MessageEvent(self.r, 
            onset, 
            instrument_name, 
            message_type=event_type, note=b2, velocity=b3, channel=channel, device_index=device_index
        )

    def cmd(self, double onset, str cmd):
        return MessageEvent(self.r, onset, cmd=cmd)

    def play(self, double onset, str instrument_name, *args, **kwargs):
        params = self._parse_params(*args, **kwargs)
        return MessageEvent(self.r, onset, instrument_name, LPMSG_PLAY, params, 0)

    def trigger(self, double onset, str instrument_name, *args, **kwargs):
        params = self._parse_params(*args, **kwargs)
        return MessageEvent(self.r, onset, instrument_name, LPMSG_TRIGGER, params, 0)

    def update(self, double onset, str instrument_name, *args, **kwargs):
        params = self._parse_params(*args, **kwargs)
        return MessageEvent(self.r, onset, instrument_name, LPMSG_UPDATE, params, 0)

    def serial(self, double onset, str tty, *args, **kwargs):
        params = self._parse_params(*args, **kwargs)
        return MessageEvent(self.r, onset, tty, LPMSG_SERIAL, params, 0)

    def udp(self, double onset, str instrument_name, *args, **kwargs):
        params = self._parse_params(*args, **kwargs)
        return MessageEvent(self.r, onset, instrument_name, LPMSG_UDP, params, 0)

    def connect(self, double onset, str instrument_name, str output, str input):
        return MessageEvent(self.r, onset, instrument_name, LPMSG_CONNECT, f'{output.strip()}\x1f{input.strip()}', 0)

    def disconnect(self, double onset, str instrument_name, str output, str input):
        return MessageEvent(self.r, onset, instrument_name, LPMSG_DISCONNECT, f'{output.strip()}\x1f{input.strip()}', 0)


cdef class SessionParamBucket:
    """ params[key] to params.key

        An interface to astrid's shared memory storage to get and set session params.
    """
    def __cinit__(self, Renderer r):
        self.r = r

    def __getattr__(self, key):
        return self.get(key)

    def get(self, str key, object default=None):
        return self.r.get_session_value(key, default)

    def __setattr__(self, str key, object value):
        self.r.set_session_value(key, value)

cdef class GraphNodeParamAccessor:
    """Accessor for a specific node's parameters in the graph.

    Allows syntax like: ctx.g.dac0.gain = 1.0
    """
    def __cinit__(self, str node_name, Renderer r):
        self.node_name = node_name
        self.r = r

    def __getattr__(self, str param_name):
        """Get a graph parameter value for this node."""
        # Construct session key: <instrument>-<node>-<param>
        key = f'{self.r.name}-{self.node_name}-{param_name}'
        return self.r.get_session_value(key, 0.0)

    def __setattr__(self, str param_name, object value):
        """Set a graph parameter value for this node."""
        # Skip internal attributes
        if param_name in ('node_name', 'r'):
            object.__setattr__(self, param_name, value)
            return

        # Construct session key: <instrument>-<node>-<param>
        key = f'{self.r.name}-{self.node_name}-{param_name}'
        self.r.set_session_value(key, value)

cdef class GraphParamBucket:
    """Bucket for graph parameter access.

    Allows syntax like: ctx.g.dac0.gain = 1.0
    """
    def __cinit__(self, Renderer r):
        self.r = r

    def __getattr__(self, str node_name):
        """Get a node accessor for the given node name."""
        return GraphNodeParamAccessor(node_name, self.r)

cdef class ParamBucket:
    """ params[key] to params.key

        These params are passed in to the render context 
        through the play message to the renderer.
    """
    def __init__(self, str play_params=None):
        self._play_params = play_params

    def __getattr__(self, key):
        return self.get(key)

    def set(self, key, value):
        if self._params is None:
            self._params = self._parse_play_params()
        self._params[key] = value

    def get(self, key, default=None):
        if key == '_params':
            return self._params
        if self._params is None:
            self._params = self._parse_play_params()
        return self._params.get(key, default)

    def _parse_play_params(self):
        cdef dict params = {}
        cdef dict _params
        cdef str t, k, v

        if self._play_params is not None:
            _params = {}
            for t in self._play_params.split(' '):
                if '=' in t:
                    t = t.strip()
                    k, v = tuple(t.split('='))
                    _params[k] = v
            params.update(_params)
        return params

cdef class MidiDeviceBucket:
    """ MIDI device interface: ctx.m(device_id).cc20 or ctx.m(device_id).note60
    
        Provides access to MIDI CC and note data stored in the session for a specific device.
        Supports both attribute access (cc20, note60) and item access ['cc20', 'note60'].
    """
    def __cinit__(self, Renderer r, int device_id, int channel=0):
        self.r = r
        self.device_id = device_id
        self.channel = channel

    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, str key, object value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, str key, object default=0):
        """ Get MIDI value by key like 'cc20' or 'note60' """
        cdef str session_key
        
        if key.startswith('cc') and key[2:].isdigit():
            cc_num = int(key[2:])
            session_key = f'midi-cc-{self.device_id}-{self.channel}-{cc_num}'
        elif key.startswith('note') and key[4:].isdigit():
            note_num = int(key[4:])
            session_key = f'midi-note-{self.device_id}-{self.channel}-{note_num}'
        else:
            raise ValueError(f"Invalid MIDI key format: {key}. Use 'ccN' or 'noteN' where N is a number.")
        
        return self.r.get_session_value(session_key, default)

    def set(self, str key, object value):
        """ Set MIDI value by key like 'cc20' or 'note60' """
        cdef str session_key
        
        if key.startswith('cc') and key[2:].isdigit():
            cc_num = int(key[2:])
            session_key = f'midi-cc-{self.device_id}-{self.channel}-{cc_num}'
        elif key.startswith('note') and key[4:].isdigit():
            note_num = int(key[4:])
            session_key = f'midi-note-{self.device_id}-{self.channel}-{note_num}'
        else:
            raise ValueError(f"Invalid MIDI key format: {key}. Use 'ccN' or 'noteN' where N is a number.")
        
        self.r.set_session_value(session_key, value)

cdef class MidiBucket:
    """ Factory for MIDI device buckets: ctx.m(device_index) -> MidiDeviceBucket
    
        Provides access to MIDI devices. Call with device index (0=first, 1=second, etc.)
        to get a device-specific interface.
    """
    def __cinit__(self, Renderer r):
        self.r = r
        # Simple mapping from device index to actual device ID
        # This gets populated when the instrument starts up
        self.device_map = {}

    def set_device_mapping(self, int device_index, int device_id):
        """ Set the mapping from device index to actual device ID """
        self.device_map[device_index] = device_id
        logger.info(f'MIDI device mapping: index {device_index} -> device ID {device_id}')

    def __call__(self, int device_index, int channel=0):
        """ Get MIDI device bucket for specific device index and channel """
        # Look up actual device ID from our mapping
        if device_index in self.device_map:
            device_id = self.device_map[device_index]
        else:
            # If no mapping, try to get it from the renderer
            if hasattr(self.r, 'midi_device_mapping') and device_index in self.r.midi_device_mapping:
                device_id = self.r.midi_device_mapping[device_index]
                self.device_map[device_index] = device_id  # Cache it
            else:
                logger.warning(f'No device mapping for index {device_index}, returning dummy device')
                device_id = -1  # Invalid device ID
            
        return MidiDeviceBucket(self.r, device_id, channel)

cdef class Seq:
    """ Interface to astrid autotrigger tables
    """
    def __cinit__(self, Renderer r):
        self.r = r

        # map the att into this ctx

    # FIXME dealloc cleanup / unmap the att

    def clear(self):
        cdef lpautotrigger_table_t * att;
        cdef astrid_shared_resource_t resource
        name_bytes = f'{self.r.name}-autotriggers'.encode('utf-8')
        cdef char * name = name_bytes
 
        if astrid_session_aquire_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.add_autotrigger: astrid_session_aquire_shared_resource could not acquire shared resource '%s'" % name.decode('utf-8'))
            return

        if resource.data == NULL:
            logger.error("Renderer.set_autotrigger: acquired resource has NULL data for '%s'" % name.decode('utf-8'))
            astrid_session_release_shared_resource(&self.r.session, &resource, name)
            return

        att = <lpautotrigger_table_t *>resource.data
        astrid_autotrigger_table_clear(att)

        if astrid_session_release_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.add_autotrigger: astrid_session_release_shared_resource could not release shared resource '%s'" % name.decode('utf-8'))
            return
 
    def set(self, int slot, double length, double speed=1, list onsets=None, str cmd=None):
        cdef double onset = 0
        cdef size_t onset_frames=0, period=0
        cdef char * cmdc = NULL
        cdef str onset_cmd = None
        cdef str override_cmd = cmd
        cdef lpautotrigger_table_t * att;
        cdef lpautotrigger_t * at;

        if onsets is None or slot < 0 or slot >= ASTRID_MAX_AUTOTRIGGERS:
            return

        period = <size_t>(length*self.r.samplerate)

        name_bytes = f'{self.r.name}-autotriggers'.encode('utf-8')
        cdef char * name = name_bytes

        # aquire the att
        cdef astrid_shared_resource_t resource
        if astrid_session_aquire_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.add_autotrigger: astrid_session_aquire_shared_resource could not acquire shared resource '%s'" % name.decode('utf-8'))
            return

        if resource.data == NULL:
            logger.error("Seq.add_autotrigger: acquired resource has NULL data for '%s'" % name.decode('utf-8'))
            astrid_session_release_shared_resource(&self.r.session, &resource, name)
            return

        att = <lpautotrigger_table_t *>resource.data

        # init the autotrigger
        at = &att.autotriggers[slot]
        astrid_autotrigger_init(at)

        logger.error(f'{onsets=}')
        for o in onsets:
            onset_cmd = None
            if len(o) == 1:
                onset = o
            elif len(o) == 2:
                onset, onset_cmd = o
            else:
                continue

            # Use override cmd if provided, otherwise per-onset cmd or default
            if override_cmd is not None:
                onset_cmd = override_cmd
            elif onset_cmd is None or len(onset_cmd) == 1:
                onset_cmd = '%s p' % self.r.name

            cmd_bytes = onset_cmd.encode('utf-8')
            cmdc = cmd_bytes

            # add onset to autotrigger
            onset_frames = <size_t>(onset * self.r.samplerate)
            astrid_autotrigger_add_onset(at, onset_frames, period, speed, cmdc)

        # update the active trigger count
        cdef bint already_active = False
        for i in range(att.num_active_triggers):
            if slot == i:
                already_active = True
                break

        if already_active == False:
            att.active_triggers[att.num_active_triggers] = slot
            att.num_active_triggers += 1;
        
        # release the att
        if astrid_session_release_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.add_autotrigger: astrid_session_release_shared_resource could not release shared resource '%s'" % name.decode('utf-8'))
            return

    def update_speed(self, int slot, double speed):
        """Update the global speed of an autotrigger without modifying onsets"""
        cdef lpautotrigger_table_t * att
        cdef lpautotrigger_t * at
        cdef astrid_shared_resource_t resource

        if slot < 0 or slot >= ASTRID_MAX_AUTOTRIGGERS:
            logger.error(f"Seq.update_speed: slot {slot} out of bounds")
            return

        if speed <= 0:
            logger.error(f"Seq.update_speed: speed must be positive (got {speed})")
            return

        name_bytes = f'{self.r.name}-autotriggers'.encode('utf-8')
        cdef char * name = name_bytes

        if astrid_session_aquire_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_speed: could not acquire shared resource '%s'" % name.decode('utf-8'))
            return

        if resource.data == NULL:
            logger.error("Seq.update_speed: acquired resource has NULL data for '%s'" % name.decode('utf-8'))
            astrid_session_release_shared_resource(&self.r.session, &resource, name)
            return

        att = <lpautotrigger_table_t *>resource.data
        at = &att.autotriggers[slot]

        if astrid_autotrigger_update_speed(at, speed) < 0:
            logger.error(f"Seq.update_speed: failed to update speed for slot {slot}")

        if astrid_session_release_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_speed: could not release shared resource '%s'" % name.decode('utf-8'))

    def update_onset_value(self, int slot, int onset_index, double onset):
        """Update the position/timing of a specific onset"""
        cdef lpautotrigger_table_t * att
        cdef lpautotrigger_t * at
        cdef astrid_shared_resource_t resource
        cdef size_t onset_frames

        if slot < 0 or slot >= ASTRID_MAX_AUTOTRIGGERS:
            logger.error(f"Seq.update_onset_value: slot {slot} out of bounds")
            return

        name_bytes = f'{self.r.name}-autotriggers'.encode('utf-8')
        cdef char * name = name_bytes

        if astrid_session_aquire_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_onset_value: could not acquire shared resource '%s'" % name.decode('utf-8'))
            return

        if resource.data == NULL:
            logger.error("Seq.update_onset_value: acquired resource has NULL data for '%s'" % name.decode('utf-8'))
            astrid_session_release_shared_resource(&self.r.session, &resource, name)
            return

        att = <lpautotrigger_table_t *>resource.data
        at = &att.autotriggers[slot]

        onset_frames = <size_t>(onset * self.r.samplerate)

        if astrid_autotrigger_update_onset_value(at, onset_index, onset_frames) < 0:
            logger.error(f"Seq.update_onset_value: failed to update onset {onset_index} for slot {slot}")

        if astrid_session_release_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_onset_value: could not release shared resource '%s'" % name.decode('utf-8'))

    def update_onset_cmd(self, int slot, int onset_index, str cmd):
        """Update the command of a specific onset"""
        cdef lpautotrigger_table_t * att
        cdef lpautotrigger_t * at
        cdef astrid_shared_resource_t resource
        cdef char * cmdc

        if slot < 0 or slot >= ASTRID_MAX_AUTOTRIGGERS:
            logger.error(f"Seq.update_onset_cmd: slot {slot} out of bounds")
            return

        name_bytes = f'{self.r.name}-autotriggers'.encode('utf-8')
        cdef char * name = name_bytes
        cmd_bytes = cmd.encode('utf-8')
        cmdc = cmd_bytes

        if astrid_session_aquire_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_onset_cmd: could not acquire shared resource '%s'" % name.decode('utf-8'))
            return

        if resource.data == NULL:
            logger.error("Seq.update_onset_cmd: acquired resource has NULL data for '%s'" % name.decode('utf-8'))
            astrid_session_release_shared_resource(&self.r.session, &resource, name)
            return

        att = <lpautotrigger_table_t *>resource.data
        at = &att.autotriggers[slot]

        if astrid_autotrigger_update_onset_cmd(at, onset_index, cmdc) < 0:
            logger.error(f"Seq.update_onset_cmd: failed to update cmd for onset {onset_index} in slot {slot}")

        if astrid_session_release_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_onset_cmd: could not release shared resource '%s'" % name.decode('utf-8'))

    def update_cmd(self, int slot, str cmd):
        """Update the command for all onsets in a trigger"""
        cdef lpautotrigger_table_t * att
        cdef lpautotrigger_t * at
        cdef astrid_shared_resource_t resource
        cdef char * cmdc

        if slot < 0 or slot >= ASTRID_MAX_AUTOTRIGGERS:
            logger.error(f"Seq.update_cmd: slot {slot} out of bounds")
            return

        name_bytes = f'{self.r.name}-autotriggers'.encode('utf-8')
        cdef char * name = name_bytes
        cmd_bytes = cmd.encode('utf-8')
        cmdc = cmd_bytes

        if astrid_session_aquire_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_cmd: could not acquire shared resource '%s'" % name.decode('utf-8'))
            return

        if resource.data == NULL:
            logger.error("Seq.update_cmd: acquired resource has NULL data for '%s'" % name.decode('utf-8'))
            astrid_session_release_shared_resource(&self.r.session, &resource, name)
            return

        att = <lpautotrigger_table_t *>resource.data
        at = &att.autotriggers[slot]

        if astrid_autotrigger_update_all_cmds(at, cmdc) < 0:
            logger.error(f"Seq.update_cmd: failed to update commands for slot {slot}")

        if astrid_session_release_shared_resource(&self.r.session, &resource, name) < 0:
            logger.error("Seq.update_cmd: could not release shared resource '%s'" % name.decode('utf-8'))

cdef class EventContext:
    def __cinit__(self, 
            Renderer r,
            str msg=None,
            int voice_id=-1,
            double max_processing_time=1,
            size_t count=0,
        ):

        cdef size_t now = 0

        self._graph = None
        self.p = ParamBucket(msg)
        self.s = SessionParamBucket(r)
        self.m = MidiBucket(r)
        self.t = EventTriggerFactory(r)
        self.r = r
        self.instrument_name = r.name

        self.seq = Seq(r)

        self.vid = voice_id
        self.count = count
        if lpscheduler_get_now_ticks(&now, <int>r.samplerate) < 0:
            logger.exception('Error getting now ticks during %s event ctx init' % r.name)
            now = 0
        elif now == 0:
            logger.warning('Scheduler returned zero ticks during %s event ctx init' % r.name)
        self.now = now

    @property
    def params(self):
        return self.p._params

    @property
    def graph(self):
        # lazy-load the ugen graph if needed
        if self._graph is None:
            from pippi.ugens import Graph
            self._graph = Graph(self.instrument_name)
        return self._graph

    @property
    def g(self):
        return GraphParamBucket(self.r)

    @property
    def io(self):
        # I/O routing -- simple wrapper for jack_connect
        if self._router is None:
            self._router = Router()
        return self._router

    @property
    def samplerate(self):
        return self.r.samplerate

    def adc(self, length=1, offset=0, channels=None):
        # FIXME channel input does nothing
        if channels is None:
            channels = self.r.input_channels
        return self.r.read_from_adc(length, offset=offset, channels=channels)

    # FIXME use the trigger factory?
    def autotrigger(self, int autotrigger_id, double freq, str cmd):
        self.r.set_autotrigger(autotrigger_id, freq, cmd)

    def load_sample(self, str name, double length=0, double offset=0, int channels=0):
        if length <= 0 and offset == 0:
            # just read the entire sample
            #logger.error(f'Reading entire sample {name}')
            return self.r.read_from_sampler(name)

        if channels <= 0:
            channels = self.r.output_channels

        # otherwise read a portion from the sample
        #logger.error(f'Reading {length=} {offset=} sample {name}')
        return self.r.read_block_from_sampler(name, length, offset=offset, channels=channels)

    def save_sample(self, str name, SoundBuffer snd):
        return self.r.save_to_sampler(name, snd)

    def dub_into_sample(self, str name, SoundBuffer snd, double offset=0, bint overdub=False, bint wrap=False):
        return self.r.write_block_into_sampler(name, snd, offset, overdub, wrap)

    def sample(self, str name, SoundBuffer snd=None, double length=0, double offset=0, int channels=2, bint overdub=False, bint wrap=False, bint overwrite=False):
        # FIXME: maybe get rid of this API, it's confusing
        if snd is None:
            return self.load_sample(name, length, offset, channels)

        # write operations
        if overwrite:        
            #logger.error(f'Overwrite sample {name}')
            return self.r.save_to_sampler(name, snd)
        else:
            #logger.error(f'Dub into sample {name} {overdub=} {wrap=}')
            return self.r.write_block_into_sampler(name, snd, offset, overdub, wrap)

    def resample(self, length=1, offset=0, channels=2, samplerate=48000, instrument=None):
        cdef str name
        if instrument is None:
            instrument = self.name
        name = '%s-resampler' % instrument

        return self.r.read_block_from_sampler(name, length, offset=offset, channels=channels)

    def log(self, msg):
        logger.info('ctx.log[%s] %s' % (self.instrument_name, msg))

    def get_params(self):
        return self.p._params

cdef class Instrument:
    def __cinit__(self):
        memset(self.ascii_name, 0, 256)
        memset(self.ascii_midi_input_device_names, 0, 8 * 256)
        memset(self.ascii_midi_output_device_names, 0, 8 * 256)

    def __init__(self, 
            str name, 
            str path, 
            int input_channels, 
            int output_channels, 
            double initial_volume,
            double adc_length, 
            double resampler_length, 
            list midi_in, 
            list midi_out,
            int is_interactive, 
            double bpm,
            bint graph_enabled=False,
            int udp_port=0
        ):
        cdef int i
        cdef lpinstrument_config_t config
        cdef bytes device_bytes, name_bytes, midi_input_bytes, midi_output_bytes


        self.name = name
        self.path = path

        name_bytes = name.encode('UTF-8')
        strncpy(self.ascii_name, name_bytes, 255)

        self.midi_input_devices = midi_in if midi_in is not None else []
        self.midi_output_devices = midi_out if midi_out is not None else []

        for i in range(min(len(self.midi_input_devices), 8)):
            device_bytes = self.midi_input_devices[i].encode('UTF-8')
            strncpy(self.ascii_midi_input_device_names[i], device_bytes, 255)

        for i in range(min(len(self.midi_output_devices), 8)):
            device_bytes = self.midi_output_devices[i].encode('UTF-8')
            strncpy(self.ascii_midi_output_device_names[i], device_bytes, 255)

        config = astrid_instrument_init_config(self.ascii_name)
        config.initial_volume = initial_volume
        config.input_channels = input_channels
        config.output_channels = output_channels

        for i in range(min(len(self.midi_input_devices), 8)):
            config.midiin_device_names[i] = self.ascii_midi_input_device_names[i]
        config.num_midiin_device_names = min(len(self.midi_input_devices), 8)

        for i in range(min(len(self.midi_output_devices), 8)):
            config.midiout_device_names[i] = self.ascii_midi_output_device_names[i]
        config.num_midiout_device_names = min(len(self.midi_output_devices), 8)

        config.adc_length = adc_length
        config.resampler_length = resampler_length
        config.ext_relay_enabled = 1
        config.is_interactive = is_interactive
        config.bpm = bpm
        config.udp_port = udp_port
        
        if graph_enabled:
            config.stream_callback = astrid_instrument_python_graph_stream_callback
            logger.info(f'Instrument {name}: configured for graph stream processing')
        
        self.config = config

    def start_running(self):
        if self.config.name == NULL:
            raise InstrumentError('Instrument config has NULL name')
            
        self.i = astrid_instrument_start_from_config(self.config)
        if self.i == NULL:
            raise InstrumentError('Could not initialize lpinstrument_t')

        if self.i.samplerate <= 0:
            astrid_instrument_stop(self.i)
            raise InstrumentError(f'Invalid sample rate from instrument: {self.i.samplerate}')
            
        if self.i.input_channels <= 0 or self.i.output_channels <= 0:
            astrid_instrument_stop(self.i)
            raise InstrumentError(f'Invalid channel configuration: in={self.i.input_channels}, out={self.i.output_channels}')

        self.samplerate = self.i.samplerate
        self.input_channels = self.i.input_channels
        self.output_channels = self.i.output_channels
        
        self.midi_device_mapping = {}
        for i in range(self.i.num_midiin_devices):
            device_id = self.i.midiin_device_ids[i]
            self.midi_device_mapping[i] = device_id
            logger.info(f'MIDI device mapping: index {i} -> device ID {device_id}')

        # Get consumer handle for relay_messages queue (to read relay messages)
        cdef bytes relay_qname_bytes = f'{self.name}-relayq'.encode('utf8')
        self.relay_msgq = astrid_msgq_consume(&self.i.session, relay_qname_bytes)
        if self.relay_msgq == NULL:
            astrid_instrument_stop(self.i)
            raise InstrumentError(f'Failed to get consumer handle for relay message queue for {self.name}')

    def __dealloc__(self):
        if self.relay_msgq != NULL:
            astrid_msgq_close(self.relay_msgq)
            self.relay_msgq = NULL

    cpdef lpmsg_t get_message(Instrument self):
        if self.i == NULL:
            raise InstrumentError('Instrument not initialized')
        if self.relay_msgq == NULL:
            raise InstrumentError('Relay message queue not initialized')
        if astrid_msgq_read(self.relay_msgq, &self.msg) < 0:
            raise InstrumentError('Could not get the instrument message')
        return self.msg

cdef class Renderer:
    def __cinit__(self, 
            int comrade_id,
            str name, 
            str path, 
            int output_channels, 
            int input_channels, 
            int samplerate,
            dict midi_device_mapping=None
        ):
        if not name or len(name) == 0:
            raise ValueError('Renderer name cannot be empty')
        if not path or len(path) == 0:
            raise ValueError('Renderer path cannot be empty')
        if output_channels <= 0:
            raise ValueError('Output channels must be positive')
        if input_channels <= 0:
            raise ValueError('Input channels must be positive')
        if samplerate <= 0:
            raise ValueError('Sample rate must be positive')
        if len(name.encode('utf8')) >= LPMAXNAME:
            raise ValueError(f'Renderer name too long: {len(name)} >= {LPMAXNAME}')
            
        self.name = name
        self.path = path
        self.output_channels = output_channels
        self.input_channels = input_channels
        self.samplerate = samplerate
        self.midi_device_mapping = midi_device_mapping if midi_device_mapping is not None else {}
        self._hash_cache = {}

        self.adcname = <char*>malloc(4096)
        if self.adcname == NULL:
            raise MemoryError("Failed to allocate memory for adcname")
        cdef bytes _adcname_bytes
        adcname = f'{name}-adc'
        _adcname_bytes = adcname.encode('utf8')
        strncpy(self.adcname, _adcname_bytes, 4095)
        self.adcname[4095] = 0

        cdef bytes instrument_name_bytes
        instrument_name_bytes = name.encode('utf8')
        strncpy(self.msg.instrument_name, instrument_name_bytes, sizeof(self.msg.instrument_name) - 1)
        self.msg.instrument_name[sizeof(self.msg.instrument_name) - 1] = 0

        self.name_hash = lphashstr(self.msg.instrument_name)

        if astrid_session_open(&self.session, self.msg.instrument_name) < 0:
            if self.adcname != NULL:
                free(self.adcname)
                self.adcname = NULL
            raise InstrumentError(f'Failed to open astrid session for {name}')

        # Get producer handle for internal_messages queue (to publish buffers)
        cdef bytes qname_bytes = f'{name}-msgq'.encode('utf8')
        self.msgq = astrid_msgq_produce(&self.session, qname_bytes, NUM_MAINMQ_PRODUCERS + comrade_id)
        if self.msgq == NULL:
            astrid_session_close(&self.session)
            if self.adcname != NULL:
                free(self.adcname)
                self.adcname = NULL
            raise InstrumentError(f'Failed to get producer handle for message queue for {name}')

        # Get consumer handle for relay_messages queue (to read relay messages)
        cdef bytes relay_qname_bytes = f'{name}-relayq'.encode('utf8')
        self.relay_msgq = astrid_msgq_consume(&self.session, relay_qname_bytes)
        if self.relay_msgq == NULL:
            astrid_msgq_close(self.msgq)
            astrid_session_close(&self.session)
            if self.adcname != NULL:
                free(self.adcname)
                self.adcname = NULL
            raise InstrumentError(f'Failed to get consumer handle for relay message queue for {name}')

        # now preload the instrument
        self.load()

    def __dealloc__(self):
        if self.msgq != NULL:
            astrid_msgq_close(self.msgq)
            self.msgq = NULL
        if self.relay_msgq != NULL:
            astrid_msgq_close(self.relay_msgq)
            self.relay_msgq = NULL
        astrid_session_close(&self.session)
        if self.adcname != NULL:
            free(self.adcname)

    @property
    def renderer(self):
        if self._renderer is None:
            self.load()
        return self._renderer

    def load(self):
        """ Loads a renderer module from the script 
            at self.path 

            Failure to load the module raises an 
            InstrumentNotFoundError
        """
        cdef char * _k
        try:
            logger.info('Loading instrument %s from %s' % (self.name, self.path))
            
            if not os.path.exists(self.path):
                raise InstrumentError(f'Instrument script not found: {self.path}')
                
            spec = importlib.util.spec_from_file_location(self.name, self.path)
            if spec is not None and spec.loader is not None:
                renderer = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(renderer)
                except Exception as e:
                    logger.exception('Renderer.load: spec.loader.exec_module error loading instrument module: %s' % str(e))
                    raise InstrumentError(f'Failed to execute instrument module: {e}') from e

                if not hasattr(renderer, '_'):
                    renderer._ = None

                self._renderer = renderer

            else:
                logger.error('Renderer.load: importlib.util.spec_from_file_location could not load instrument - spec is None: %s %s' % (self.path, self.name))
                raise InstrumentError(f'Instrument renderer has a null spec for {self.name} at {self.path}')

        except TypeError as e:
            logger.exception('Renderer.load: TypeError loading renderer module: %s' % str(e))
            raise InstrumentError(f'TypeError loading the python renderer {self.name}: {e}') from e
        except Exception as e:
            logger.exception('Renderer.load: Unexpected error loading renderer module: %s' % str(e))
            raise InstrumentError(f'Unexpected error loading the python renderer {self.name}: {e}') from e

        logger.debug('loaded instrument, setting metadata')
        self.last_reload = os.path.getmtime(self.path)

    cpdef void set_autotrigger(Renderer self, int autotrigger_id, double freq, str cmd):
        cmd_byte_string = cmd.encode('utf-8')
        cdef char * _cmd = cmd_byte_string
        cdef astrid_shared_resource_t resource
        cdef char name[NAME_MAX]
        memset(name, 0, NAME_MAX)

        instrument_name_bytes = self.name.encode('utf-8')
        cdef char * instrument_name = instrument_name_bytes
        
        snprintf(name, NAME_MAX, "%s-autotriggers", instrument_name)
        
        if astrid_session_aquire_shared_resource(&self.session, &resource, name) < 0:
            logger.error("Renderer.set_autotrigger: astrid_session_aquire_shared_resource could not acquire shared resource '%s'" % name.decode('utf-8'))
            return
        
        if resource.data == NULL:
            logger.error("Renderer.set_autotrigger: acquired resource has NULL data for '%s'" % name.decode('utf-8'))
            astrid_session_release_shared_resource(&self.session, &resource, name)
            return
        
        cdef lpautotrigger_t * autotriggers = <lpautotrigger_t*>resource.data
        
        #astrid_autotrigger_set_freq(&autotriggers[autotrigger_id], freq, _cmd)
        
        if astrid_session_release_shared_resource(&self.session, &resource, name) < 0:
            logger.error("Renderer.set_autotrigger: astrid_session_release_shared_resource could not release shared resource '%s'" % name.decode('utf-8'))
            return
        
        logger.info("astrid_instrument_set_autotrigger_from_id released")

    cpdef EventContext get_event_context(Renderer self):
        return EventContext.__new__(EventContext,
            self,
            msg=self.msg.msg.decode('ascii'),
            voice_id=self.msg.voice_id,
            max_processing_time=self.max_processing_time,
            count=self.msg.count,
        )

    cdef SoundBuffer read_from_adc(Renderer self, double length, double offset=0, int channels=2, int samplerate=48000):
        if length <= 0:
            raise ValueError('ADC read length must be positive')
        if offset < 0:
            raise ValueError('ADC read offset must be non-negative')
        if channels <= 0:
            raise ValueError('ADC read channels must be positive')

        cdef size_t offset_in_frames = <size_t>(offset * samplerate)

        cdef SoundBuffer out = SoundBuffer(length=length, channels=self.input_channels, samplerate=samplerate)

        if astrid_session_read_shared_ringbuffer_block(&self.session, self.adcname, offset_in_frames, out.buffer) < 0:
            logger.error('Renderer.read_from_adc: astrid_session_read_shared_ringbuffer_block failed to read %d frames at offset %d from ADC' % (int(length*samplerate), offset_in_frames))

        return out

    cpdef object get_session_value(Renderer self, str key, object default=None):
        cdef bytes keybytes = key.encode('ascii')
        cdef char * _key = keybytes
        cdef astrid_shared_resource_header_t header
        cdef astrid_shared_resource_t resource
        cdef bytes valb
        cdef lpfloat_t valf = 0
        cdef lpint_t vali = 0
        cdef object val = None
        cdef char val_cstring[LPMAXMSG]
        cdef lpbuffer_t * val_buffer

        if AstridSession.get_info(&self.session, _key, &header) < 0:
            return default

        if header.type == ASTRID_TYPE_FLOAT:
            memcpy(&valf, header.value, header.size)
            val = valf

        elif header.type == ASTRID_TYPE_INT:
            memcpy(&vali, header.value, header.size)
            val = vali

        elif header.type == ASTRID_TYPE_STRING:
            memcpy(val_cstring, header.value, LPMAXMSG)
            valb = val_cstring
            val = valb.decode('ascii')

        elif header.type == ASTRID_TYPE_BUFFER:
            val_buffer = AstridSession.get_buffer(&self.session, _key)
            val = SoundBuffer._fromlpbuffer(val_buffer)

        elif header.type == ASTRID_TYPE_BYTES:
            if astrid_session_aquire_shared_resource(&self.session, &resource, _key) < 0:
                logger.debug(f'Renderer.get_session_value: astrid_session_aquire_shared_resource could not acquire shared resource for {key}')
                return default

            if resource.data == NULL:
                logger.error(f'Renderer.get_session_value: acquired resource has NULL data for {key}')
                astrid_session_release_shared_resource(&self.session, &resource, _key)
                return default

            valb = (<char *>resource.data)[:resource.header.size]
            val = pickle.loads(valb)

            if astrid_session_release_shared_resource(&self.session, &resource, _key) < 0:
                logger.error(f'Renderer.get_session_value: astrid_session_release_shared_resource could not release shared resource for session value {key}')

        else:
            logger.error(f'Renderer.get_session_value: unknown session value type {header.type} for {key}')
            return default

        return val

    cdef int write_to_internal_queue(Renderer self, lpmsg_t * msg):
        if self.msgq == NULL:
            logger.error('write_to_internal_queue: message queue not initialized')
            return -1
        return astrid_msgq_write(self.msgq, msg)

    cpdef void set_session_value(Renderer self, str key, object value):
        cdef bytes keybytes = key.encode('ascii')
        cdef char * _key = keybytes
        cdef astrid_shared_resource_header_t header
        cdef lpfloat_t valf = 0
        cdef lpint_t vali = 0
        cdef object val = None
        cdef bytes valb
        cdef char * valc
        cdef char val_cstring[LPMAXMSG]
        cdef size_t blen
        cdef SoundBuffer val_soundbuffer

        if isinstance(value, numbers.Integral):
            vali = <lpint_t>value
            AstridSession.set_int(&self.session, _key, vali)

        elif isinstance(value, numbers.Real):
            valf = <lpfloat_t>value
            AstridSession.set_float(&self.session, _key, valf)

        elif isinstance(value, str):
            valb = value.encode('ascii')
            valc = valb
            blen = len(valb)
            blen = blen if blen <= LPMAXMSG else LPMAXMSG # copy at most LPMAXMSG bytes
            memcpy(val_cstring, valc, blen)
            AstridSession.set_string(&self.session, _key, val_cstring)

        elif isinstance(value, SoundBuffer):
            val_soundbuffer = <SoundBuffer>value
            AstridSession.set_buffer(&self.session, _key, val_soundbuffer.buffer)

        else:
            try:
                valb = pickle.dumps(value)
                blen = len(valb)
                valc = valb
                if astrid_session_register_shared_resource(&self.session, _key, valc, ASTRID_TYPE_BYTES, blen) < 0:
                    logger.error(f'Renderer.set_session_value: astrid_session_register_shared_resource could not register shared resource for session value {key}')
            except pickle.PicklingError as e:
                logger.error(f'Renderer.set_session_value: could not pickle {value}')

    cpdef void set_session_param_hash(Renderer self, str key, double value):
        """Set a graph parameter using hash-based session API.

        This computes the hash of the key (or retrieves from cache) and writes
        directly to the session using the same mechanism as graph creation.
        """
        cdef bytes keybytes
        cdef char * _key
        cdef uint32_t key_hash
        cdef lpfloat_t valf = <lpfloat_t>value

        # Try cache first (fast path)
        try:
            key_hash = self._hash_cache[key]
        except KeyError:
            # Compute hash and cache it
            keybytes = key.encode('ascii')
            _key = keybytes
            key_hash = lphashstr(_key)
            self._hash_cache[key] = key_hash

        AstridSession.set_float_from_hash(&self.session, key_hash, valf)

    def _init_graph_params(self, graph):
        """Initialize parameter values for all graph nodes from their definitions.

        For each node in the graph, read the parameter values that were set in add_node()
        kwargs and write them to the session only if not already set.

        This is called after stream() creates the graph but before sending the
        GRAPH_UPDATE_READY message, ensuring defaults are available when the C code
        creates the ugen graph.
        """
        from pippi.ugens import UGEN_CONNECTIONS, UGEN_TYPES
        cdef bytes keybytes
        cdef char * _key
        cdef uint32_t key_hash
        cdef int exists

        for node_name, node in graph.nodes.items():
            ugen_type_name = node.ugen_name

            if ugen_type_name not in UGEN_TYPES:
                continue

            ugen_type_int = UGEN_TYPES[ugen_type_name]

            # Get the inputs spec for this ugen type
            if ugen_type_name not in UGEN_CONNECTIONS:
                continue

            inputs = UGEN_CONNECTIONS[ugen_type_name].get('inputs', {})

            # For each parameter that was set in add_node() kwargs
            for param_name, value in node.params.items():
                if param_name not in inputs:
                    continue

                param_index = inputs[param_name]

                # Construct the session key
                key = f'{self.name}-{node_name}-{ugen_type_int}-{param_index}'

                # Compute hash once and use hash-based APIs
                keybytes = key.encode('ascii')
                _key = keybytes
                key_hash = lphashstr(_key)

                # Check if the key exists in the session using hash
                exists = AstridSession.exists_from_hash(&self.session, key_hash)

                # Only set if the key doesn't exist yet
                if not exists:
                    AstridSession.set_float_from_hash(&self.session, key_hash, <lpfloat_t>value)

    def handle_update_message(self, str msgstr):
        cdef EventContext ctx 
        cdef dict params
        cdef str p, k, v
        
        if not msgstr:
            logger.warning('handle_update_message: empty message string for %s' % self.name)
            return

        try:
            ctx = self.get_event_context()
        except Exception as e:
            logger.error('handle_update_message: failed to get event context for %s: %s' % (self.name, e))
            return
            
        params = dict()

        try:
            # read msg body, split and call update with each
            for p in msgstr.split(' '):
                if '=' in p:
                    p = p.strip()
                    parts = p.split('=', 1)  # Split on first '=' only to handle values with '='
                    if len(parts) != 2:
                        logger.warning('handle_update_message: malformed param %s in %s' % (p, self.name))
                        continue
                    k, v = tuple(parts)
                    v = v.strip()
                    k = k.strip()
                else:
                    v = None
                    k = p.strip()
                    if k == '':
                        continue

                if not k:
                    logger.warning('handle_update_message: empty key in %s' % self.name)
                    continue

                # update the param in the session if it exists
                try:
                    setattr(ctx.s, k, v)
                except Exception as e:
                    logger.error('handle_update_message: failed to set session param %s=%s in %s: %s' % (k, v, self.name, e))

                # invoke the update callback on the instrument if there is one
                if hasattr(self.renderer, 'update'):
                    try:
                        self.renderer.update(ctx, k, v)
                    except Exception as e:
                        logger.exception('Error during %s update handler for param %s=%s: %s' % (self.name, k, v, e))

        except Exception as e:
            logger.exception('Error during %s update message handling: %s' % (self.name, e))

    def handle_midi_message(self, char * payload):
        cdef EventContext ctx
        cdef size_t offset = 0
        cdef unsigned char device_index=0, mtype=0, mid=0, mval=0

        if payload == NULL:
            logger.error('handle_midi_message: NULL payload for %s' % self.name)
            return

        if not hasattr(self.renderer, 'midi_messages'):
            logger.warning('Ignoring MIDI message: instrument %s has no midi_messages callback registered' % self.name)
            return

        if lpmidi_decode_eventbytes(payload, &device_index, &mtype, &mid, &mval) < 0:
            logger.error('handle_midi_message: failed to decode MIDI event bytes for %s' % self.name)
            return

        try:
            ctx = self.get_event_context()
        except Exception as e:
            logger.error('handle_midi_message: failed to get event context for %s: %s' % (self.name, e))
            return

        try:
            self.renderer.midi_messages(ctx, device_index, mtype, mid, mval)
        except Exception as e:
            logger.exception('Error during %s midi_messages handler for device_index=%d mtype=%d mid=%d mval=%d: %s' % (self.name, device_index, mtype, mid, mval, e))

cdef tuple collect_players(Renderer r):
    loop = False
    # FIXME it's still nice to support this, but 
    # it should just schedule a message instead of 
    # storing a flag on the serialized buffer...
    if hasattr(r.renderer, 'LOOP'):
        loop = r.renderer.LOOP

    # find all play functions
    players = set()

    # The simplest case is a single play function
    if hasattr(r.renderer, 'play'):
        players.add(r.renderer.play)

    # Play functions can also be registered via 
    # an @player.init decorator
    if hasattr(r.renderer, 'player') \
        and hasattr(r.renderer.player, 'players') \
        and isinstance(r.renderer.player.players, set):
        players |= r.renderer.player.players

    # Finally, any compatible function can be added to a set
    if hasattr(r.renderer, 'PLAYERS') \
        and isinstance(r.renderer.PLAYERS, set):
        players |= r.renderer.PLAYERS
    
    return players, loop

cdef int render_event(Renderer r):
    cdef set players
    cdef bint loop
    cdef bytes bufstr
    cdef int _channel_map[256]
    cdef int map_channels = 0
    cdef EventContext ctx 
    cdef size_t grid_interval=0, grid_offset=0
    cdef object snd
    cdef SoundBuffer _snd

    ctx = r.get_event_context()

    if hasattr(r.renderer, 'before'):
        r.renderer.before(ctx)

    players, loop = collect_players(r)

    for player in players:
        try:
            snd = player(ctx)
            map_channels = 0
            if isinstance(snd, tuple) and len(snd) == 2:
                channel_map, _snd = snd
                if isinstance(channel_map, int):
                    map_channels = 1
                    _channel_map[0] = channel_map
                else:
                    map_channels = len(channel_map)
                    for i in range(map_channels):
                        _channel_map[i] = channel_map[i]
            else:
                _snd = snd

            if snd is None:
                continue

            _snd.moved = True # claim the memory so it doesn't get freed by the cython destructor
            if astrid_session_publish_buffer(&r.session, r.msgq, _snd.buffer, map_channels, _channel_map) < 0:
                logger.error(f'render_event: astrid_session_publish_buffer render publish failed for {r.name}')
                _snd.moved = False # let cython clean things up
                continue  # Skip this render, try next player

        except Exception as e:
            logger.exception('render_event: error during %s render: %s' % (r.name, e))
            # Don't return error for individual player failures, continue with other players
            continue

    if hasattr(r.renderer, 'done'):
        r.renderer.done(ctx)

    return 0

cdef set collect_trigger_planners(Renderer r):
    # FIXME -- this can be consolodated into some 
    # kind of named callback parser...

    # find all trigger planner functions
    planners = set()

    # The simplest case is a single trigger function
    if hasattr(r.renderer, 'trigger'):
        planners.add(r.renderer.trigger)

    # Trigger functions can also be registered via 
    # a @triggerer.init decorator
    if hasattr(r.renderer, 'triggerer') \
        and hasattr(r.renderer.triggerer, 'planners') \
        and isinstance(r.renderer.triggerer.planners, set):
        planners |= r.renderer.triggerer.planners

    # Finally, any compatible function can be added to a set
    if hasattr(r.renderer, 'TRIGGERERS') \
        and isinstance(r.renderer.TRIGGERERS, set):
        planners |= r.renderer.TRIGGERERS
    
    return planners

cdef bytes serialize_lpmsg(lpmsg_t msg):
    cdef unsigned char * msgp = <unsigned char *>&msg
    return msgp[:sizeof(lpmsg_t)]

cdef void deserialize_lpmsg(bytes msgb, lpmsg_t * msg):
    memcpy(msg, <char*>msgb, sizeof(lpmsg_t))

cdef int trigger_events(Renderer r):
    """ Collect the trigger functions in the instrument module
        and compute the triggers to be scheduled.
    """
    cdef set planners
    cdef bint loop
    cdef EventContext ctx 
    cdef list eventlist
    cdef int qfd
    cdef size_t now = 0
    #cdef bytes trigger_params = r.msg.msg
    cdef list trigger_events = []

    ctx = r.get_event_context()

    logger.debug('trigger generation event %s w/params %s' % (str(r), r.msg.msg))

    if hasattr(r.renderer, 'trigger_before'):
        r.renderer.trigger_before(ctx)

    # Collect the planners and collate the triggers
    planners = collect_trigger_planners(r)

    for p in planners:
        try:
            eventlist = p(ctx)
            if eventlist is None:
                continue
            trigger_events += eventlist
        except Exception as e:
            logger.exception('Error during %s trigger generation: %s' % (ctx.r.name, e))
            return 1

    # Schedule the trigger events
    logger.error('Scheduling %d trigger events: %s' % (len(trigger_events), trigger_events))

    if lpscheduler_get_now_ticks(&now, <int>r.samplerate) < 0:
        logger.exception('Error getting now ticks during %s trigger scheduling' % r.name)
        now = 0
    elif now == 0:
        logger.warning('Scheduler returned zero ticks during %s trigger scheduling' % r.name)

    logger.error(f't {now=}')
    for t in trigger_events:
        if t is None:
            logger.debug('Got null trigger in event list')
            continue
        if t.schedule(now) < 0:
            logger.exception('Error trying to schedule event from %s trigger generation' % r.name)
        logger.debug('Scheduled event %s' % t)

    if hasattr(r.renderer, 'trigger_done'):
        r.renderer.trigger_done(ctx)

    return 0

def render_executor(
        str name,
        str path,
        int output_channels,
        int input_channels,
        int samplerate,
        object q,
        int comrade_id,
        dict midi_device_mapping
    ):
    cdef size_t last_edit
    cdef double start=0, end=0
    cdef int mtype = 0
    cdef lpmsg_t msg
    cdef bytes msgb

    # Prevent multiple processes from sharing the same seed
    dsp.seed(time.time() + comrade_id)

    cdef Renderer r = Renderer(comrade_id, name, path, output_channels, input_channels, samplerate, midi_device_mapping)

    while True:
        msgb = q.get()
        deserialize_lpmsg(msgb, &msg)
        r.msg = msg

        if msg.type == LPMSG_SHUTDOWN:
            logger.info('Renderer comrade %d shutting down' % comrade_id)
            break

        last_edit = os.path.getmtime(r.path)
        if not r._renderer or last_edit > r.last_reload:
            logger.info('render_executor load()')
            r.load()

        if msg.type == LPMSG_PLAY:
            #logger.error(f'PLAY {msg.type=} {msg.msg=} {comrade_id=}')
            if lpscheduler_get_now_seconds(&start) < 0:
                logger.exception('Error getting start time for render timing')
                start = 0

            if render_event(r) < 0:
                logger.exception('Error during render event execution for %s' % r.name)
                continue  # Don't exit, try to continue processing

            if lpscheduler_get_now_seconds(&end) < 0:
                logger.exception('Error getting end time for render timing')
                end = start  # Use start time to avoid negative duration
            r.max_processing_time = max(r.max_processing_time, end - start)
            #logger.debug('%s render time: %f seconds' % (r.name, end - start))

        elif msg.type == LPMSG_TRIGGER:
            trigger_events(r)
                

def relay_messages_to_comrades(
        double samplerate,
        str script_path,
        str instrument_name,
        int input_channels,
        int output_channels,
        int is_interactive,
        double initial_volume,
        double adc_length,
        double resampler_length,
        object q,
        bint graph_enabled,
        dict midi_device_mapping
    ):
    cdef size_t last_edit
    cdef lpmsg_t msg
    cdef EventContext ctx

    logger.info(f'PY: running forever... {script_path=} {instrument_name=}')

    cdef Renderer r = Renderer(MAINMQ_PY_INSTRUMENT_PRODUCER, instrument_name, script_path, output_channels, input_channels, samplerate, midi_device_mapping)
    logger.info('init preload()')
    r.load()

    # set up the autotriggers
    ctx = r.get_event_context()
    if hasattr(r.renderer, 'seq'):
        try:
            logger.info(f'PY: SEQ INIT')
            ctx.seq.clear()
            r.renderer.seq(ctx)
        except Exception as e:
            logger.exception('comrade message relay: renderer.seq error with autotrigger init: %s' % str(e))

    # run the onload callback
    if hasattr(r.renderer, 'onload'):
        try:
            r.renderer.onload(ctx)
        except Exception as e:
            logger.exception('comrade message relay: renderer.onload error executing onload callback: %s' % str(e))

    # or the stream
    if hasattr(r.renderer, 'stream'):
        try:
            r.renderer.stream(ctx)
            if ctx.graph is not None:
                # Serialize graph and send update message
                logger.info(f'Renderer.load: sending graph update for {instrument_name}')
                logger.info(f'{ctx.graph=}')

                # Initialize default parameter values in session for all nodes
                # Only set if the parameter is not already set (check for null/0)
                r._init_graph_params(ctx.graph)

                MessageEvent(r, 0, instrument_name, LPMSG_GRAPH_UPDATE_READY, graph=ctx.graph).schedule(ctx.now)
        except Exception as e:
            logger.exception('Renderer.load: renderer.stream error creating stream graph: %s' % str(e))

    while True:
        try:
            if astrid_msgq_read(r.relay_msgq, &msg) == 1:
                # Queue empty, sleep briefly and retry
                time.sleep(0.001)
                continue
        except Exception as e:
            logger.exception(f'Unexpected error reading message: {e}')
            continue

        if msg.type == LPMSG_SHUTDOWN:
            logger.info('PY MSG: shutdown')
            for _ in range(NUM_COMRADES):
                q.put(serialize_lpmsg(msg))
            return

        if msg.type == LPMSG_UPDATE:
            r.handle_update_message(msg.msg.decode('utf-8'))

        elif msg.type == LPMSG_MIDI_FROM_DEVICE:
            r.handle_midi_message(msg.msg)

        else:
            #logger.info(f'PY MSG: {msg.msg} ({msg.type})')
            q.put(serialize_lpmsg(msg))

        last_edit = os.path.getmtime(r.path)
        if last_edit > r.last_reload:
            logger.info('(p)reload()')
            r.load()
            ctx = r.get_event_context()
            if hasattr(r.renderer, 'seq'):
                try:
                    ctx.seq.clear()
                    r.renderer.seq(ctx)
                except Exception as e:
                    logger.exception('comrade message relay: renderer.seq error with autotrigger init: %s' % str(e))

            if hasattr(r.renderer, 'onload'):
                try:
                    r.renderer.onload(ctx) 
                except Exception as e:
                    logger.exception('comrade message relay: renderer.onload error executing onload callback: %s' % str(e))

            if hasattr(r.renderer, 'stream'):
                try:
                    r.renderer.stream(ctx)
                    if ctx.graph is not None:
                        # Serialize graph and send update message
                        logger.info(f'Renderer.load: sending graph update for {instrument_name}')
                        logger.info(f'{ctx.graph=}')
                        MessageEvent(r, 0, instrument_name, LPMSG_GRAPH_UPDATE_READY, graph=ctx.graph).schedule(ctx.now)
                except Exception as e:
                    logger.exception('Renderer.load: renderer.stream error creating stream graph: %s' % str(e))

    logger.info('PY: python instrument shutting down...')

def run_forever(
        str script_path, 
        str instrument_name=None, 
        int channels=-1, 
        int input_channels=2, 
        int output_channels=2, 
        double adc_length=60, 
        double resampler_length=60, 
        double initial_volume=1,
        list midi_in=None, 
        list midi_out=None,
        int is_interactive=1,
        bint graph_enabled=False,
        double bpm=-1,
        int udp_port=0,
    ):
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    mp.set_start_method('spawn')
    cdef Instrument instrument = None
    instrument_name = instrument_name if instrument_name is not None else Path(script_path).stem
    instrument_byte_string = instrument_name.encode('UTF-8')
    cdef char * _instrument_ascii_name = instrument_byte_string

    if channels > 0:
        input_channels = channels
        output_channels = channels

    try:
        # Start the stream and setup the instrument
        logger.info(f'PY: loading python instrument... {script_path=} {instrument_name=} {midi_in=} {midi_out=}')
        instrument = Instrument(
            instrument_name, 
            script_path, 
            input_channels, 
            output_channels,
            initial_volume,
            adc_length, 
            resampler_length, 
            midi_in, 
            midi_out,
            is_interactive,
            bpm,
            graph_enabled,
            udp_port,
        )
        instrument.start_running()
        logger.info(f'PY: started instrument... {script_path=} {instrument_name=}')
        
        # Create MIDI device mapping
        midi_device_mapping = {}
        for i in range(instrument.i.num_midiin_devices):
            device_id = instrument.i.midiin_device_ids[i]
            midi_device_mapping[i] = device_id
            logger.info(f'MIDI device mapping: index {i} -> device ID {device_id}')
    except InstrumentError as e:
        logger.error('PY: Error trying to start instrument. Shutting down...')
        return

    render_pool = []
    render_q = SimpleQueue()
    for i in range(NUM_COMRADES):
        logger.error(f'{i=} RENDER EXECUTOR STARTING PROCESS')
        comrade = Process(target=render_executor, args=(
            instrument_name, 
            script_path, 
            instrument.i.output_channels, 
            instrument.i.input_channels, 
            instrument.i.samplerate, 
            render_q, 
            i,
            midi_device_mapping
        ))
        comrade.start()
        render_pool += [ comrade ]

    message_process = Process(target=relay_messages_to_comrades, args=(
        instrument.samplerate,
        script_path,
        instrument_name,
        input_channels,
        output_channels,
        is_interactive,
        initial_volume,
        adc_length,
        resampler_length,
        render_q,
        graph_enabled,
        midi_device_mapping
    ))
    message_process.start()

    try:
        while instrument.i.is_running:
            # Read messages from the console and relay them to the q
            # yields periodically for render pool cleanup
            if astrid_instrument_tick(instrument.i) < 0:
                logger.error('PY: Could not read console line, instrument may be shutting down')
                if not instrument.i.is_running:
                    logger.info('PY: Instrument stopped running, breaking main loop')
                    break
                time.sleep(0.2)
                continue

    except KeyboardInterrupt as e:
        pass

    print('Shutting down...')
    message_process.join()
    for r in render_pool:
        r.join()
    print('All done! See you later!')
