#cython: language_level=3

from pippi.soundbuffer cimport SoundBuffer

cdef extern from "pippicore.h":
    ctypedef double lpfloat_t
    cdef enum Wavetables:
        WT_SINE,
        WT_COS,
        WT_SQUARE, 
        WT_TRI, 
        WT_TRI2, 
        WT_SAW,
        WT_RSAW,
        WT_RND,
        WT_USER,
        NUM_WAVETABLES

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
        WIN_HAMM,
        WIN_BART,
        WIN_BLACK,
        WIN_SINC,
        WIN_GAUSS,
        WIN_GAUSSIN,
        WIN_GAUSSOUT,
        WIN_PLUCKIN, 
        WIN_PLUCKOUT, 
        WIN_RND,
        WIN_SAW,
        WIN_RSAW,
        WIN_USER,
        NUM_WINDOWS

    cdef enum PanMethods:
        PANMETHOD_CONSTANT,
        PANMETHOD_LINEAR,
        PANMETHOD_SINE,
        PANMETHOD_GOGINS,
        NUM_PANMETHODS

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

    ctypedef struct lpwavetable_factory_t:
        lpbuffer_t * (*create)(int name, size_t length)
        void (*destroy)(lpbuffer_t *)

    ctypedef struct lpwindow_factory_t:
        lpbuffer_t * (*create)(int name, size_t length)
        void (*destroy)(lpbuffer_t *)

    ctypedef struct lpmemorypool_t:
        unsigned char * pool
        size_t poolsize
        size_t pos

    ctypedef struct lpmemorypool_factory_t:
        unsigned char * pool
        size_t poolsize
        size_t pos

        void (*init)(unsigned char *, size_t)
        lpmemorypool_t * (*custom_init)(unsigned char *, size_t)
        void * (*alloc)(size_t, size_t)
        void * (*custom_alloc)(lpmemorypool_t *, size_t, size_t)
        void (*free)(void *)

    ctypedef struct lpinterpolation_factory_t:
        lpfloat_t (*linear_pos)(lpbuffer_t *, lpfloat_t)
        lpfloat_t (*linear)(lpbuffer_t *, lpfloat_t)
        lpfloat_t (*linear_channel)(lpbuffer_t *, lpfloat_t, int)
        lpfloat_t (*hermite_pos)(lpbuffer_t *, lpfloat_t)
        lpfloat_t (*hermite)(lpbuffer_t *, lpfloat_t)

    ctypedef struct lpbuffer_factory_t: 
        lpbuffer_t * (*create)(size_t, int, int)
        lpbuffer_t * (*create_from_float)(lpfloat_t, size_t, int, int)
        lpbuffer_t * (*create_from_bytes)(char *, size_t, int, int)
        void (*copy)(lpbuffer_t *, lpbuffer_t *)
        lpbuffer_t * (*clone)(lpbuffer_t *)
        void (*clear)(lpbuffer_t *)
        void (*split2)(lpbuffer_t *, lpbuffer_t *, lpbuffer_t *)
        void (*scale)(lpbuffer_t *, lpfloat_t, lpfloat_t, lpfloat_t, lpfloat_t)
        lpfloat_t (*min)(lpbuffer_t * buf)
        lpfloat_t (*max)(lpbuffer_t * buf)
        lpfloat_t (*mag)(lpbuffer_t * buf)
        lpfloat_t (*avg)(lpbuffer_t * buf)
        lpfloat_t (*play)(lpbuffer_t *, lpfloat_t)
        void (*pan)(lpbuffer_t * buf, lpbuffer_t * pos, int method)
        lpbuffer_t * (*mix)(lpbuffer_t *, lpbuffer_t *)
        lpbuffer_t * (*remix)(lpbuffer_t *, int)
        void (*remap)(lpbuffer_t * dest, lpbuffer_t * src, int map_channels, int * channel_map)
        void (*clip)(lpbuffer_t * buf, lpfloat_t minval, lpfloat_t maxval)
        lpbuffer_t * (*cut)(lpbuffer_t * buf, size_t start, size_t length)
        void (*cut_into)(lpbuffer_t * buf, lpbuffer_t * out, size_t start, size_t length)
        lpbuffer_t * (*varispeed)(lpbuffer_t * buf, lpbuffer_t * speed)
        lpbuffer_t * (*resample)(lpbuffer_t *, size_t)
        void (*multiply)(lpbuffer_t *, lpbuffer_t *)
        void (*multiply_scalar)(lpbuffer_t *, lpfloat_t)
        void (*add)(lpbuffer_t *, lpbuffer_t *)
        void (*add_scalar)(lpbuffer_t *, lpfloat_t)
        void (*subtract)(lpbuffer_t *, lpbuffer_t *)
        void (*subtract_scalar)(lpbuffer_t *, lpfloat_t)
        void (*divide)(lpbuffer_t *, lpbuffer_t *)
        void (*divide_scalar)(lpbuffer_t *, lpfloat_t)
        void (*diff)(lpbuffer_t *, lpbuffer_t *)
        lpbuffer_t * (*concat)(lpbuffer_t *, lpbuffer_t *)
        int (*buffers_are_equal)(lpbuffer_t *, lpbuffer_t *)
        int (*buffers_are_close)(lpbuffer_t *, lpbuffer_t *, int)
        void (*dub)(lpbuffer_t *, lpbuffer_t *, size_t)
        void (*dub_into)(lpbuffer_t * buf, lpbuffer_t * src, size_t offset, lpfloat_t feedback, int wrap, int overdub)
        void (*dub_scalar)(lpbuffer_t *, lpfloat_t, size_t)
        lpfloat_t (*env_process)(lpbuffer_t * env, lpfloat_t freq)
        void (*env)(lpbuffer_t *, lpbuffer_t *)
        lpbuffer_t * (*pad)(lpbuffer_t * buf, size_t before, size_t after)
        void (*taper)(lpbuffer_t * buf, size_t start, size_t end)
        lpbuffer_t * (*trim)(lpbuffer_t * buf, size_t start, size_t end, lpfloat_t threshold, int window)
        lpbuffer_t * (*fadein)(lpbuffer_t * buf, lpfloat_t amount)
        lpbuffer_t * (*fadeout)(lpbuffer_t * buf, lpfloat_t amount)
        void (*fill)(lpbuffer_t * buf, lpbuffer_t * src, int nperiods);
        lpbuffer_t * (*loop)(lpbuffer_t * src, size_t length)
        lpbuffer_t * (*repeat)(lpbuffer_t * src, size_t repeats)
        lpbuffer_t * (*reverse)(lpbuffer_t * buf)
        lpbuffer_t * (*resize)(lpbuffer_t *, size_t)
        void (*plot)(lpbuffer_t * buf)
        void (*destroy)(lpbuffer_t *)

    ctypedef struct lprand_t:
        lpfloat_t logistic_seed
        lpfloat_t logistic_x

        lpfloat_t lorenz_timestep
        lpfloat_t lorenz_x
        lpfloat_t lorenz_y
        lpfloat_t lorenz_z
        lpfloat_t lorenz_a
        lpfloat_t lorenz_b
        lpfloat_t lorenz_c

        void (*preseed)()
        void (*seed)(int)

        lpfloat_t (*stdlib)(lpfloat_t, lpfloat_t)
        lpfloat_t (*logistic)(lpfloat_t, lpfloat_t)

        lpfloat_t (*lorenz)(lpfloat_t, lpfloat_t)
        lpfloat_t (*lorenzX)(lpfloat_t, lpfloat_t)
        lpfloat_t (*lorenzY)(lpfloat_t, lpfloat_t)
        lpfloat_t (*lorenzZ)(lpfloat_t, lpfloat_t)

        lpfloat_t (*rand_base)(lpfloat_t, lpfloat_t)
        lpfloat_t (*rand)(lpfloat_t, lpfloat_t)
        int (*randint)(int, int)
        int (*randbool)()
        int (*choice)(int)

    extern lprand_t LPRand
    extern const lpbuffer_factory_t LPBuffer
    extern const lpwavetable_factory_t LPWavetable 
    extern const lpwindow_factory_t LPWindow
    extern lpmemorypool_factory_t LPMemoryPool
    extern const lpinterpolation_factory_t LPInterpolation


cdef double _mag(double[:,:] snd)
cpdef double mag(SoundBuffer snd)
cpdef list scale(list source, double tolow=*, double tohigh=*, double fromlow=*, double fromhigh=*, bint log=*)
cpdef double scalef(double source, double tolow=*, double tohigh=*, double fromlow=*, double fromhigh=*, bint log=*, bint exp=*)
cpdef list snap(list source, double mult=*, object pattern=*)
cpdef double tolog(double value, int base=*)
cpdef double toexp(double value, int base=*)
cpdef SoundBuffer mix(list sounds, align_end=*)
cpdef SoundBuffer randline(int numpoints, double lowvalue=*, double highvalue=*, int wtsize=*)
cpdef SoundBuffer wt(object values, object lowvalue=*, object highvalue=*, int wtsize=*)
cpdef list ws(object values=*, object crossings=*, int offset=*, int limit=*, int modulo=*)
cpdef SoundBuffer win(object values, object lowvalue=*, object highvalue=*, int wtsize=*)
cpdef SoundBuffer stack(list sounds)
cpdef SoundBuffer buffer(object frames=*, double length=*, int channels=*, int samplerate=*)
cpdef SoundBuffer bufferfrom(SoundBuffer src)
cpdef SoundBuffer read(object filename, double length=*, double start=*)
cpdef list readall(str path, double length=*, double start=*)
cpdef SoundBuffer readchoice(str path)
cpdef double rand(double low=*, double high=*)
cpdef int randint(int low=*, int high=*)
cpdef object choice(list choices)
cpdef void seed(object value=*)
cpdef void randmethod(str method=*)
cpdef dict randdump()
cpdef SoundBuffer render(list events, object callback, int channels=*, int samplerate=*)
