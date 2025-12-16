from pippi.soundbuffer cimport lpfloat_t, lpbuffer_t, lpbuffer_factory_t, LPBuffer, Wavetables, WT_SINE, WT_COS, WT_TRI, WT_SAW, WT_RSAW, WT_RND, WT_SQUARE

cdef extern from "pippicore.h":
    ctypedef struct lpstack_t:
        lpbuffer_t ** stack
        size_t length
        lpfloat_t phase
        lpfloat_t pos
        int read_index

    ctypedef struct lpwavetable_factory_t:
        lpbuffer_t * (*create)(int name, size_t length)
        lpstack_t * (*create_stack)(int numtables, ...)
        void (*destroy)(lpbuffer_t*)

    extern const lpwavetable_factory_t LPWavetable

cdef extern from "oscs.bln.h":
    ctypedef struct lpblnosc_t:
        lpfloat_t phase
        lpfloat_t phaseinc
        lpfloat_t freq
        lpfloat_t minfreq
        lpfloat_t maxfreq
        lpfloat_t samplerate
        lpbuffer_t * buf
        int gate

    ctypedef struct lpblnosc_factory_t:
        lpblnosc_t * (*create)(lpbuffer_t *, lpfloat_t, lpfloat_t)
        lpfloat_t (*process)(lpblnosc_t *)
        lpbuffer_t * (*render)(lpblnosc_t *, size_t, lpbuffer_t *, int)
        void (*destroy)(lpblnosc_t *)

    extern const lpblnosc_factory_t LPBLNOsc


