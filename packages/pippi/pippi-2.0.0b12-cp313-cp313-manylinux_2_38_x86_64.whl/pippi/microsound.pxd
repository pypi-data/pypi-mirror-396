cdef extern from "pippicore.h":
    cdef enum Windows:
        WIN_NONE,
        WIN_SINE,
        WIN_SINEIN,
        WIN_SINEOUT,
        WIN_COS,
        WIN_TRI, 
        WIN_PHASOR, 
        WIN_HANN, 
        WIN_HANNIN, 
        WIN_HANNOUT, 
        WIN_RND,
        WIN_SAW,
        WIN_RSAW,
        WIN_USER,
        NUM_WINDOWS

    ctypedef double lpfloat_t

    ctypedef struct lpbuffer_t:
        size_t length
        int samplerate
        int channels
        lpfloat_t phase
        size_t boundry
        size_t range
        size_t pos
        size_t onset
        int is_looping
        lpfloat_t data[]

    ctypedef struct lpbuffer_factory_t:
        lpbuffer_t * (*create)(size_t, int, int)
        void (*copy)(lpbuffer_t *, lpbuffer_t *)
        lpfloat_t (*min)(lpbuffer_t * buf)
        lpfloat_t (*max)(lpbuffer_t * buf)
        lpfloat_t (*mag)(lpbuffer_t * buf)
        lpfloat_t (*avg)(lpbuffer_t * buf)
        void (*destroy)(lpbuffer_t *)

    ctypedef struct lpwindow_factory_t:
        lpbuffer_t * (*create)(int name, size_t length)
        void (*destroy)(lpbuffer_t*)

    ctypedef struct lpinterpolation_factory_t:
        lpfloat_t (*linear_pos)(lpbuffer_t *, lpfloat_t);
        lpfloat_t (*linear_pos2)(lpfloat_t *, size_t, lpfloat_t);
        lpfloat_t (*linear)(lpbuffer_t *, lpfloat_t);
        lpfloat_t (*linear_channel)(lpbuffer_t *, lpfloat_t, int);
        lpfloat_t (*hermite_pos)(lpbuffer_t *, lpfloat_t);
        lpfloat_t (*hermite)(lpbuffer_t *, lpfloat_t);

    extern const lpbuffer_factory_t LPBuffer
    extern const lpwindow_factory_t LPWindow
    extern const lpinterpolation_factory_t LPInterpolation

cdef extern from "microsound.h":
    ctypedef struct lpgrain_t:
        size_t length
        int channels
        lpfloat_t samplerate
        lpfloat_t pulsewidth 
        lpfloat_t grainlength
        lpfloat_t offset
        lpfloat_t pan
        lpfloat_t amp
        lpfloat_t speed
        lpfloat_t skew
        int gate

    ctypedef struct lpformation_t:
        lpgrain_t grains[4096]
        lpgrain_t * active_grains[4096]
        lpfloat_t grainlength
        lpfloat_t grainlength_maxjitter
        lpfloat_t grainlength_jitter
        lpfloat_t grid_maxjitter
        lpfloat_t grid_jitter
        int numgrains
        lpfloat_t spread
        lpfloat_t speed
        lpfloat_t length
        size_t offset
        lpfloat_t interval
        lpfloat_t phaseinc
        lpfloat_t phase
        int gate
        lpfloat_t skew
        lpfloat_t amp
        lpfloat_t pan
        lpfloat_t pulsewidth
        lpbuffer_t * source
        lpbuffer_t * window
        lpbuffer_t * current_frame

    ctypedef struct lpformation_factory_t:
        lpformation_t * (*create)(lpbuffer_t * src, lpbuffer_t * win)
        void (*init)(lpformation_t *)
        void (*update_interval)(lpformation_t *, lpfloat_t new_interval)
        void (*increment_offset)(lpformation_t *)
        void (*process)(lpformation_t *)
        void (*destroy)(lpformation_t *)

    extern const lpformation_factory_t LPFormation

cdef class Formation:
    cdef unsigned int channels
    cdef unsigned int samplerate

    cdef public list onsets
    cdef bint track_onsets

    cdef lpbuffer_t * win

    cdef lpformation_t * formation

    cdef lpbuffer_t * amp
    cdef lpbuffer_t * offset
    cdef lpbuffer_t * pulsewidth
    cdef lpbuffer_t * grainlength
    cdef lpbuffer_t * grainmaxjitter
    cdef lpbuffer_t * grainjitter
    cdef lpbuffer_t * gridmaxjitter
    cdef lpbuffer_t * gridjitter
    cdef lpbuffer_t * position
    cdef lpbuffer_t * speed
    cdef lpbuffer_t * spread
    cdef lpbuffer_t * grid

    cdef bint gridincrement
