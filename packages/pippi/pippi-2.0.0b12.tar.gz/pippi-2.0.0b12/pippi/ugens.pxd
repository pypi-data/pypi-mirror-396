#cython: language_level=3

from pippi.soundbuffer cimport *

cdef extern from "oscs.sine.h":
    ctypedef struct lpsineosc_t:
        lpfloat_t phase
        lpfloat_t freq
        lpfloat_t samplerate
        
cdef extern from "oscs.tape.h":
    ctypedef struct lptapeosc_t:
        lpfloat_t phase
        lpfloat_t speed
        lpfloat_t pulsewidth
        lpfloat_t samplerate
        lpfloat_t start
        lpfloat_t start_increment
        lpfloat_t range
        lpbuffer_t * buf
        lpbuffer_t * current_frame
        int gate

cdef extern from "oscs.pulsar.h":
    ctypedef struct lppulsarosc_t:
        lpfloat_t * wavetables
        size_t wavetable_length
        int num_wavetables
        size_t * wavetable_onsets
        size_t * wavetable_lengths
        lpfloat_t wavetable_morph
        lpfloat_t wavetable_morph_freq

        lpfloat_t * windows
        size_t window_length
        int num_windows
        size_t * window_onsets
        size_t * window_lengths
        lpfloat_t window_morph
        lpfloat_t window_morph_freq

        #bool * burst
        size_t burst_size
        size_t burst_pos 

        lpfloat_t phase
        lpfloat_t saturation
        lpfloat_t pulsewidth
        lpfloat_t samplerate
        lpfloat_t freq


cdef extern from "ugens.core.h":
    cdef enum UgenTypes:
        UGEN_SINE,
        UGEN_TAPE,
        UGEN_ADC,
        UGEN_DAC,
        UGEN_MIX,
        UGEN_MULT,
        UGEN_PULSAR,
        NUM_UGEN_TYPES

    cdef enum UgenParams:
        # Basic parameters
        UPARAM_FREQ,
        UPARAM_PHASE, 
        UPARAM_AMP,
        UPARAM_GAIN,
        UPARAM_SPEED,
        UPARAM_CHANNEL,
        UPARAM_PULSEWIDTH,
        
        # Mult parameters
        UPARAM_A,
        UPARAM_B,

        # DAC parameters
        UPARAM_INPUT,

        # Tape parameters
        UPARAM_BUF,
        UPARAM_START,
        UPARAM_RANGE,
        
        # ADC parameters
        UPARAM_SMOOTHING,
        
        # Pulsar wavetable parameters
        UPARAM_WAVETABLES,
        UPARAM_WAVETABLE_LENGTH,
        UPARAM_NUM_WAVETABLES,
        UPARAM_WAVETABLE_OFFSETS,
        UPARAM_WAVETABLE_LENGTHS,
        UPARAM_WAVETABLE_MORPH,
        UPARAM_WAVETABLE_MORPH_FREQ,
        
        # Pulsar window parameters
        UPARAM_WINDOWS,
        UPARAM_WINDOW_LENGTH,
        UPARAM_NUM_WINDOWS,
        UPARAM_WINDOW_OFFSETS,
        UPARAM_WINDOW_LENGTHS,
        UPARAM_WINDOW_MORPH,
        UPARAM_WINDOW_MORPH_FREQ,
        
        # Pulsar burst parameters
        UPARAM_BURST,
        UPARAM_BURST_SIZE,
        UPARAM_BURST_POS,
        
        # Pulsar other parameters
        UPARAM_SATURATION,
        UPARAM_SAMPLERATE,
        
        NUM_UGEN_PARAMS

    ctypedef struct ugen_t:
        int type
        lpfloat_t output
        lpfloat_t outputs[8]
        int num_outputs
        
        # Direct parameter connections to other ugens
        ugen_t * param_sources[16]  # NUM_UGEN_PARAMS
        lpfloat_t param_mults[16]   # NUM_UGEN_PARAMS
        lpfloat_t param_adds[16]    # NUM_UGEN_PARAMS
        lpfloat_t param_values[16]  # NUM_UGEN_PARAMS

    ctypedef struct ugen_factory_t:
        ugen_t * (*create)(char * instrument_name, char * node_name, int ugen_type)
        lpfloat_t (*process)(ugen_t * u)
        void (*connect)(ugen_t * u, int param, ugen_t * source, lpfloat_t mult, lpfloat_t add)
        void (*set_param)(ugen_t * u, int param, lpfloat_t value)
        void (*set_param_buffer)(ugen_t * u, int param, lpbuffer_t * buffer)
        lpfloat_t (*get_output)(ugen_t * u, int index)
        void (*destroy)(ugen_t * u)

    extern const ugen_factory_t LPUgen

    lpfloat_t lpugen_get_param(ugen_t * u, int param)

    void lpugen_adc_set_input_sample(ugen_t * u, lpfloat_t sample)
    lpfloat_t lpugen_adc_get_level(ugen_t * u)
    lpfloat_t lpugen_adc_get_peak(ugen_t * u)


cdef class Node:
    cdef ugen_t * u
    cdef str ugen_name
    cdef str name
    cdef public dict connection_map
    cdef public object connections
    cdef public dict params  # Track parameter values set via kwargs
    cdef double mult
    cdef double add
    cdef list _allocated_buffers  # Track buffers we need to free

cdef class Graph:
    cdef public dict nodes
    cdef object outputs
    cdef list _node_strings     # Track serialized nodes
    cdef list _connection_strings  # Track serialized connections
    cdef str _instrument_name   # Instrument name for session key generation
    cdef object _session        # Session reference for set_param
    cdef double next_sample(Graph self)
