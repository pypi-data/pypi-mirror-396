#cython: language_level=3

from pippi.soundbuffer cimport *

#ctypedef double (*osc_interp_point_t)(double[:] data, double point, BLIData* bl_data) nogil

cdef extern from "oscs.pulsar.h":
    ctypedef struct lppulsarosc_t:
        lpbuffer_t * wavetables[4096]
        int num_wavetables;
        lpfloat_t wavetable_morph;
        lpfloat_t wavetable_morph_freq;

        lpbuffer_t * windows[4096];
        int num_windows;
        lpfloat_t window_morph;
        lpfloat_t window_morph_freq;

        bint burst[4096];
        bint saturation_toggle;
        size_t burst_size;
        size_t burst_pos; 

        bint once;
        bint pulse_edge;
        lpfloat_t phase;
        lpfloat_t saturation;
        lpfloat_t pulsewidth;
        lpfloat_t samplerate;
        lpfloat_t freq;

    ctypedef struct lppulsarosc_factory_t:
        lppulsarosc_t * (*create)();
        int (*add_wavetable)(lppulsarosc_t * osc, lpbuffer_t * wt);
        int (*add_window)(lppulsarosc_t * osc, lpbuffer_t * win);
        void (*burst_file)(lppulsarosc_t * osc, char * filename, size_t burst_size);
        void (*burst_bytes)(lppulsarosc_t * osc, unsigned char * bytes, size_t burst_size);
        lpfloat_t (*process)(lppulsarosc_t *);
        void (*destroy)(lppulsarosc_t*);

    cdef extern const lppulsarosc_factory_t LPPulsarOsc;


"""
cdef class Bar:
    cdef public double[:] amp
    cdef public double decay
    cdef public double stiffness
    cdef public double leftclamp
    cdef public double rightclamp
    cdef public double scan
    cdef public double barpos
    cdef public double velocity
    cdef public double width
    cdef public double loss

    cdef public int channels
    cdef public int samplerate
    cdef public int wtsize

    cdef SoundBuffer _play(self, int length)
"""


cdef class FM:
    cdef lpbuffer_t * freq
    cdef lpbuffer_t * ratio
    cdef lpbuffer_t * index 
    cdef lpbuffer_t * amp
    cdef lpbuffer_t * carrier
    cdef lpbuffer_t * modulator

    #cdef interp_point_t freq_interpolator

    cdef double freq_phase
    cdef double ratio_phase
    cdef double index_phase
    cdef double amp_phase
    cdef double cwt_phase
    cdef double mwt_phase

    cdef public int channels
    cdef public int samplerate
    cdef public int wtsize


cdef class Osc:
    cdef lpbuffer_t * freq
    cdef lpbuffer_t * amp
    cdef lpbuffer_t * wavetable
    cdef lpbuffer_t * pm

    #cdef interp_point_t freq_interpolator

    cdef double freq_phase
    cdef double amp_phase
    cdef double wt_phase
    cdef double pm_phase

    cdef public int channels
    cdef public int samplerate
    cdef public int wtsize

    cdef lpbli_t * bl_data

    #cdef osc_interp_point_t interp_method

"""
cdef class Osc2d:
    cdef public double[:] freq
    cdef public double[:] amp

    cdef interp_point_t freq_interpolator

    cdef list wavetables
    cdef public double lfo_freq
    cdef object lfo

    cdef double[:] window
    cdef public double pulsewidth

    cdef double[:] mod
    cdef public double mod_range
    cdef public double mod_freq

    cdef public double phase
    cdef public double win_phase
    cdef public double mod_phase
    cdef double freq_phase
    cdef double amp_phase

    cdef public int channels
    cdef public int samplerate
    cdef public int wtsize

    cdef object _play2d(self, int length)
"""

cdef class Pulsar2d:
    cdef lppulsarosc_t * osc
    cdef lpbuffer_t * freq
    cdef lpbuffer_t * amp
    cdef lpbuffer_t * pulsewidth

    cdef lpbuffer_t * mask
    cdef public long[:] burst

    cdef list wavetables
    cdef list windows

    #cdef interp_point_t freq_interpolator

    cdef int wt_count
    cdef int wt_length
    cdef double wt_pos
    cdef double wt_phase
    cdef double wt_mod_phase
    cdef lpbuffer_t * wt_mod

    cdef int win_count
    cdef int win_length
    cdef double win_pos
    cdef double win_phase
    cdef double win_mod_phase
    cdef lpbuffer_t * win_mod

    cdef double freq_phase
    cdef double pw_phase
    cdef double amp_phase
    cdef double mask_phase
    cdef double burst_phase
    cdef int burst_length

    cdef public int channels
    cdef public int samplerate


cdef class DelayLine:
    cdef short[:] buf
    cdef int position

cdef class Pluck:
    cdef DelayLine upper_rail
    cdef DelayLine lower_rail

    cdef double amp
    cdef double freq
    cdef double pick
    cdef double pickup

    cdef short state
    cdef int pickup_location
    cdef int rail_length
    cdef lpbuffer_t * seed

    cdef int samplerate
    cdef int channels


    cpdef short get_sample(Pluck self, DelayLine dline, int position)
    cpdef double next_sample(Pluck self)
    cpdef SoundBuffer play(Pluck self, double length, object seed=*)


cdef class SineOsc:
    cdef lpbuffer_t * freq
    cdef lpbuffer_t * amp

    #cdef interp_point_t freq_interpolator

    cdef double freq_phase
    cdef double amp_phase
    cdef double osc_phase

    cdef public int channels
    cdef public int samplerate
    cdef public int wtsize


cdef class Tukey:
    cdef lpbuffer_t * shape
    cdef lpbuffer_t * freq
    cdef lpbuffer_t * amp

    cdef double phase

    cdef public int channels
    cdef public int samplerate

    #cdef interp_pos_t freq_interpolator

    cpdef SoundBuffer play(Tukey self, double length=*)

