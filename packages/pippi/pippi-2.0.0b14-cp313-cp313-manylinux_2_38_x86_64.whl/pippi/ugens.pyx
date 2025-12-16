from collections import defaultdict
import warnings

cimport numpy as np
import numpy as np

from pippi import dsp
from pippi.defaults cimport DEFAULT_SAMPLERATE, DEFAULT_CHANNELS
from pippi.soundbuffer cimport SoundBuffer

np.import_array()

# Make these regular Python dicts so they're accessible at runtime from render processes
UGEN_TYPES = {
    'sine':   UGEN_SINE,
    'mult':   UGEN_MULT,
    'tape':   UGEN_TAPE,
    'adc':    UGEN_ADC,
    'dac':    UGEN_DAC,
    'mix':    UGEN_MIX,
    'pulsar': UGEN_PULSAR
}

UGEN_CONNECTIONS = {
    'sine': {
        'inputs': {
            'freq': UPARAM_FREQ,
            'phase': UPARAM_PHASE,
        },
        'outputs': {
            'out': 0,       # Main sine wave output
            'freq': 1,      # Current frequency value
            'phase': 2,     # Current phase value
        },
    },
    'mult': {
        'inputs': {
            'a': UPARAM_A,
            'b': UPARAM_B,
        },
        'outputs': {
            'out': 0,       # result
            'a': 1,         # passthrough
            'b': 2,
        }
    },
    'tape': {
        'inputs': {
            'speed': UPARAM_SPEED,
            'phase': UPARAM_PHASE,
            'buf': UPARAM_BUF,
            'start': UPARAM_START,
            'range': UPARAM_RANGE,
        },
        'outputs': {
            'out': 0,       # Main tape playback output
            'speed': 1,     # Current speed value
            'phase': 2,     # Current phase/position
            'gate': 3,      # Gate signal output
        }
    },
    'adc': {
        'inputs': {
            'gain': UPARAM_GAIN,
            'smoothing': UPARAM_SMOOTHING,
            'channel': UPARAM_CHANNEL,
        },
        'outputs': {
            'out': 0,       # Main ADC input signal
            'level': 1,     # Smoothed level detection
            'peak': 2,      # Peak level detection
            'gain': 3,      # Current gain value
            'channel': 4,   # Channel number
        }
    },
    'dac': {
        'inputs': {
            'in': UPARAM_INPUT,      # Input signal
            'gain': UPARAM_GAIN,
            'channel': UPARAM_CHANNEL,
        },
        'outputs': {
            'out': 0,       # Main DAC output signal
            'gain': 1,      # Current gain value
            'channel': 2,   # Channel number
        }
    },
    'mix': {
        'inputs': {
            'gain': UPARAM_GAIN,
            'channel': UPARAM_CHANNEL,
        },
        'outputs': {
            'out': 0,       # Main MIX output signal (from async mixer)
            'gain': 1,      # Current gain value
            'channel': 2,   # Channel number
        }
    },
    'pulsar': {
        'inputs': {
            'freq': UPARAM_FREQ,
            'phase': UPARAM_PHASE,
            'pulsewidth': UPARAM_PULSEWIDTH,
            'saturation': UPARAM_SATURATION,
            'samplerate': UPARAM_SAMPLERATE,

            'wavetables': UPARAM_WAVETABLES,
            'wavetable_length': UPARAM_WAVETABLE_LENGTH,
            'num_wavetables': UPARAM_NUM_WAVETABLES,
            'wavetable_offsets': UPARAM_WAVETABLE_OFFSETS,
            'wavetable_lengths': UPARAM_WAVETABLE_LENGTHS,
            'wavetable_morph': UPARAM_WAVETABLE_MORPH,
            'wavetable_morph_freq': UPARAM_WAVETABLE_MORPH_FREQ,

            'windows': UPARAM_WINDOWS,
            'window_length': UPARAM_WINDOW_LENGTH,
            'num_windows': UPARAM_NUM_WINDOWS,
            'window_offsets': UPARAM_WINDOW_OFFSETS,
            'window_lengths': UPARAM_WINDOW_LENGTHS,
            'window_morph': UPARAM_WINDOW_MORPH,
            'window_morph_freq': UPARAM_WINDOW_MORPH_FREQ,

            'burst': UPARAM_BURST,
            'burst_size': UPARAM_BURST_SIZE,
            'burst_pos': UPARAM_BURST_POS,
        },
        'outputs': {
            'out': 0,            # Main pulsar output
            'freq': 1,           # Current frequency
            'phase': 2,          # Current phase
            'pulsewidth': 3,     # Current pulsewidth
            'saturation': 4,     # Current saturation
            'samplerate': 5,     # Current samplerate
            # Wavetable outputs
            'wavetable_morph': 6,
            'wavetable_morph_freq': 7,
            # Window outputs  
            'window_morph': 8,
            'window_morph_freq': 9,
            # Burst outputs
            'burst_size': 10,
            'burst_pos': 11,
        }
    },
}


cdef class Node:
    def __cinit__(self, str name, str ugen, str instrument_name=None, *args, **kwargs):
        if ugen not in UGEN_TYPES:
            raise AttributeError('Invalid ugen type "%s"' % ugen)

        # Use empty string if no instrument name provided
        if instrument_name is None:
            instrument_name = ""

        instrument_bytes = instrument_name.encode('utf-8')
        cdef char * instrument_cstr = instrument_bytes
        name_bytes = name.encode('utf-8')
        cdef char * name_cstr = name_bytes
        self.u = LPUgen.create(instrument_cstr, name_cstr, UGEN_TYPES[ugen])

        self.ugen_name = ugen
        self.name = name
        self.connections = defaultdict(list)
        self.connection_map = UGEN_CONNECTIONS[ugen]
        self._allocated_buffers = []
        self.params = {}

        for k, v in kwargs.items():
            self.set_param(k, v)
            # Store non-buffer params for later access
            if 'buf' not in k:
                self.params[k] = v

    def __dealloc__(self):
        # Free all buffers we allocated
        cdef lpbuffer_t * buf
        for buf_ptr in self._allocated_buffers:
            buf = <lpbuffer_t*><size_t>buf_ptr
            if buf != NULL:
                LPBuffer.destroy(buf)

        if self.u != NULL:
            LPUgen.destroy(self.u)

    def get_output(self, str name):
        cdef int outlet_index = self.connection_map['outputs'].get(name, 0)
        return LPUgen.get_output(self.u, outlet_index)

    def set_param(self, str name, object value):
        cdef lpbuffer_t * out
        cdef size_t i
        cdef int c
        cdef int inlet_index = self.connection_map['inputs'].get(name, -1)
        
        if inlet_index == -1:
            raise ValueError(f"Unknown parameter: {self.ugen_name}.{name}")

        if 'buf' in name:
            out = LPBuffer.create(len(value), value.channels, value.samplerate)
            self._allocated_buffers.append(<size_t>out)
            for i in range(out.length):
                for c in range(out.channels):
                    out.data[i * out.channels + c] = value.frames[i,c]
            LPUgen.set_param_buffer(self.u, inlet_index, out)

        elif 'wavetables' in name:
            stack = []
            for b in value:
                if isinstance(b, str):
                    b = dsp.wt(b)
                stack += [dsp.buffer(b)]
            stack = dsp.join(stack)

            out = LPBuffer.create(len(stack), 1, stack.samplerate)
            self._allocated_buffers.append(<size_t>out)
            for i in range(out.length):
                out.data[i] = stack.frames[i,0]
            LPUgen.set_param_buffer(self.u, inlet_index, out)

            # Also set related parameters (lengths, offsets, etc.)
            LPUgen.set_param(self.u, self.connection_map['inputs'].get('wavetable_length', 0), <lpfloat_t>len(stack))

        elif 'windows' in name:
            # Handle window stack
            # FIXME eh...
            stack = []
            for b in value:
                if isinstance(b, str):
                    b = dsp.win(b)
                stack += [dsp.buffer(b)]
            stack = dsp.join(stack)

            out = LPBuffer.create(len(stack), 1, stack.samplerate)
            self._allocated_buffers.append(<size_t>out)
            for i in range(out.length):
                out.data[i] = stack.frames[i,0]
            LPUgen.set_param_buffer(self.u, inlet_index, out)

        else:
            LPUgen.set_param(self.u, inlet_index, <lpfloat_t>value)

    def process(self):
        return LPUgen.process(self.u)


cdef class Graph:
    def __cinit__(self, str instrument_name=None):
        self.nodes = {}
        self.outputs = defaultdict(float)
        self._node_strings = []
        self._connection_strings = []
        self._instrument_name = instrument_name

    def add_node(self, str name, str ugen, *args, **kwargs):
        self.nodes[name] = Node(name, ugen, self._instrument_name, *args, **kwargs)
        
        # Build serialized node string: "name:type:param1=value1,param2=value2"
        if kwargs:
            param_strs = []
            for param_name, param_value in kwargs.items():
                param_strs.append(f"{param_name}={param_value}")
            node_str = f"{name}:{ugen}:{','.join(param_strs)}"
        else:
            node_str = f"{name}:{ugen}"
        
        self._node_strings.append(node_str)

    def connect(self, str a, str b, object outmin=None, object outmax=None, double inmin=-1, double inmax=1, object mult=None, object add=None):
        cdef double _mult = 1
        cdef double _add = 0

        anodename, aportname = tuple(a.split('.'))
        bnodename, bportname = tuple(b.split('.'))

        if outmin is not None and outmax is not None:
            _mult = (outmax - outmin) / (inmax - inmin)
            _add = outmin - inmin * _mult

        if mult is not None:
            _mult = mult

        if add is not None:
            _add = add

        self.nodes[anodename].connections[aportname] += [(bnodename, bportname, _mult, _add)]
        
        # Build serialized connection string: "source.port->target.port*mult+add"
        conn_str = f"{anodename}.{aportname}->{bnodename}.{bportname}"
        
        # Add modifiers if not default values
        if _mult != 1.0:
            conn_str += f"*{_mult}"
        if _add != 0.0:
            conn_str += f"+{_add}"
        
        self._connection_strings.append(conn_str)

    def __str__(self):
        """Return the serialized graph format for message transmission"""
        node_part = ' '.join(self._node_strings)
        if self._connection_strings:
            return f"{node_part} | {' '.join(self._connection_strings)}"
        else:
            return node_part

    cdef double next_sample(Graph self):
        cdef double sample = 0

        # first process all the nodes
        for _, node in self.nodes.items():
            node.process()

            # connect the outputs to the inputs
            for portname, connections in node.connections.items():
                port = node.get_output(portname)
                for connode, conport, mult, add in connections:
                    value = port * mult + add
                    if connode == 'main' and conport == 'output':
                        sample += value
                    else:
                        self.nodes[connode].set_param(conport, value)

        return sample

    def render(Graph self, double length, int samplerate=DEFAULT_SAMPLERATE, int channels=DEFAULT_CHANNELS):
        cdef size_t framelength = <size_t>(length * samplerate)
        cdef double sample = 0
        cdef size_t i
        cdef int c

        cdef lpbuffer_t * out = LPBuffer.create(framelength, channels, samplerate)

        for i in range(framelength):
            sample = 0

            # first process all the nodes
            for _, node in self.nodes.items():
                node.process()

                # connect the outputs to the inputs
                for portname, connections in node.connections.items():
                    port = node.get_output(portname)
                    for connode, conport, mult, add in connections:
                        value = port * mult + add
                        if connode == 'main' and conport == 'output':
                            sample += value
                        else:
                            self.nodes[connode].set_param(conport, value)

            for c in range(channels):
                out.data[i * channels + c] = sample

        return SoundBuffer._fromlpbuffer(out)

