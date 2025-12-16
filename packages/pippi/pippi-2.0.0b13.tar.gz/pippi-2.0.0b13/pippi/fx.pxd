#cython: language_level=3
#clib soundpipe

from pippi.soundbuffer cimport (
    SoundBuffer, 
    LPBuffer, 
    LPMemoryPool, 
    LPInterpolation, 
    LPFilter,
    LPFX,
    lpbuffer_t, 
    lpbli_t,
    lpfloat_t, 
    lpsvf_t, 
    lpbalance_t,
    lpbfilter_t,

    FILTER_LOWPASS,
    FILTER_BANDPASS,
    FILTER_HIGHPASS,
    FILTER_NOTCH,
    FILTER_PEAK,
    FILTER_BELL,
    FILTER_LOWSHELF,
    FILTER_HIGHSHELF,
)

from libc.stdint cimport uint32_t, int64_t

cdef extern from "soundpipe.h":
    ctypedef struct sp_data:
        double* out;
        int sr
        int nchan
        unsigned long len
        unsigned long pos
        char filename[200]
        uint32_t rand

    int sp_create(sp_data**)
    int sp_destroy(sp_data**)
    int sp_process(sp_data*, void*, void (*callback)(sp_data*, void*))

    ctypedef struct sp_auxdata:
        size_t size
        void* ptr

    ctypedef struct sp_bar:
        double bcL
        double bcR
        double iK
        double ib
        double scan
        double T30
        double pos
        double vel
        double wid
        double* w
        double* w1
        double* w2
        int step
        int first
        double s0
        double s1
        double s2
        double t0
        double t1
        sp_auxdata w_aux

    int sp_bar_create(sp_bar**)
    int sp_bar_destroy(sp_bar**)
    int sp_bar_init(sp_data*, sp_bar*, double iK, double ib)
    int sp_bar_compute(sp_data*, sp_bar*, double*, double*)

    ctypedef struct sp_compressor:
        void* faust
        int argpos
        double* args[4]
        double* ratio
        double* thresh
        double* atk
        double* rel

    int sp_compressor_create(sp_compressor**)
    int sp_compressor_destroy(sp_compressor**)
    int sp_compressor_init(sp_data*, sp_compressor*)
    int sp_compressor_compute(sp_data*, sp_compressor*, double*, double*)

    ctypedef struct sp_dcblock:
        double gg
        double outputs
        double inputs
        double gain

    int sp_dcblock_create(sp_dcblock**)
    int sp_dcblock_destroy(sp_dcblock**)
    int sp_dcblock_init(sp_data*, sp_dcblock*)
    int sp_dcblock_compute(sp_data*, sp_dcblock*, double*, double*);

    ctypedef struct sp_ftbl:
        pass

    int sp_ftbl_create(sp_data*, sp_ftbl**, size_t)
    int sp_ftbl_init(sp_data*, sp_ftbl*, size_t)
    int sp_ftbl_bind(sp_data*, sp_ftbl**, double*, size_t)
    int sp_ftbl_destroy(sp_ftbl**)
    int sp_gen_vals(sp_data*, sp_ftbl*, const char*)
    int sp_gen_sine(sp_data*, sp_ftbl*)
    int sp_gen_file(sp_data*, sp_ftbl*, const char*)
    int sp_gen_sinesum(sp_data*, sp_ftbl*, const char*)
    int sp_gen_line(sp_data*, sp_ftbl*, const char*)
    int sp_gen_xline(sp_data*, sp_ftbl*, const char*)
    int sp_gen_gauss(sp_data*, sp_ftbl*, double, uint32_t)
    int sp_ftbl_loadfile(sp_data*, sp_ftbl**, const char*)
    int sp_ftbl_loadspa(sp_data*, sp_ftbl**, const char*)
    int sp_gen_composite(sp_data*, sp_ftbl*, const char*)
    int sp_gen_rand(sp_data*, sp_ftbl*, const char*)
    int sp_gen_triangle(sp_data*, sp_ftbl*)

    ctypedef struct sp_paulstretch:
        pass

    int sp_paulstretch_create(sp_paulstretch**)
    int sp_paulstretch_destroy(sp_paulstretch**)
    int sp_paulstretch_init(sp_data*, sp_paulstretch*, sp_ftbl*, double windowsize, double stretch);
    int sp_paulstretch_compute(sp_data*, sp_paulstretch*, double*, double*);

    ctypedef struct sp_saturator:
        double drive
        double dcoffset
        double dcblocker[2][7]
        double ai[6][7]
        double aa[6][7]

    int sp_saturator_create(sp_saturator**)
    int sp_saturator_destroy(sp_saturator**)
    int sp_saturator_init(sp_data*, sp_saturator*);
    int sp_saturator_compute(sp_data*, sp_saturator*, double*, double*);

    ctypedef struct sp_mincer:
        double time
        double amp
        double pitch
        sp_ftbl* ft

    int sp_mincer_create(sp_mincer**)
    int sp_mincer_destroy(sp_mincer**)
    int sp_mincer_init(sp_data*, sp_mincer*, sp_ftbl*, int)
    int sp_mincer_compute(sp_data*, sp_mincer*, double*, double*)

    ctypedef struct sp_fold:
        pass

    ctypedef struct sp_bitcrush:
        double bitdepth
        double srate
        sp_fold* fold

    int sp_bitcrush_create(sp_bitcrush**)
    int sp_bitcrush_destroy(sp_bitcrush**)
    int sp_bitcrush_init(sp_data*, sp_bitcrush*)
    int sp_bitcrush_compute(sp_data*, sp_bitcrush*, double*, double*)

    ctypedef struct sp_butlp:
        double sr, freq, istor
        double lkf
        double a[8]
        double pidsr

    int sp_butlp_create(sp_butlp**)
    int sp_butlp_destroy(sp_butlp**)
    int sp_butlp_init(sp_data*, sp_butlp*)
    int sp_butlp_compute(sp_data*, sp_butlp*, double*, double*)

    ctypedef struct sp_buthp:
        double sr, freq, istor
        double lkf
        double a[8]
        double pidsr

    int sp_buthp_create(sp_buthp**)
    int sp_buthp_destroy(sp_buthp**)
    int sp_buthp_init(sp_data*, sp_buthp*)
    int sp_buthp_compute(sp_data*, sp_buthp*, double*, double*)

    ctypedef struct sp_butbp:
        double sr, freq, istor
        double lkf
        double a[8]
        double pidsr

    int sp_butbp_create(sp_butbp**)
    int sp_butbp_destroy(sp_butbp**)
    int sp_butbp_init(sp_data*, sp_butbp*)
    int sp_butbp_compute(sp_data*, sp_butbp*, double*, double*)

    ctypedef struct sp_butbr:
        double sr, freq, istor
        double lkf
        double a[8]
        double pidsr

    int sp_butbr_create(sp_butbr**)
    int sp_butbr_destroy(sp_butbr**)
    int sp_butbr_init(sp_data*, sp_butbr*)
    int sp_butbr_compute(sp_data*, sp_butbr*, double*, double*)

    ctypedef struct sp_bal:
        double asig, csig, ihp
        double c1, c2, prvq, prvr, prva

    int sp_bal_create(sp_bal**)
    int sp_bal_destroy(sp_bal**)
    int sp_bal_init(sp_data*, sp_bal*)
    int sp_bal_compute(sp_data*, sp_bal*, double*, double*, double*)

cdef extern from "spectral.h":
    ctypedef struct lpspectral_factory_t:
        lpbuffer_t * (*convolve)(lpbuffer_t *, lpbuffer_t *);

    extern const lpspectral_factory_t LPSpectral;

cdef extern from "fx.softclip.h":
    ctypedef struct lpfxsoftclip_t:
        lpfloat_t lastval

    ctypedef struct lpfxsoftclip_factory_t:
        lpfxsoftclip_t * (*create)()
        lpfloat_t (*process)(lpfxsoftclip_t * sc, lpfloat_t val)
        void (*destroy)(lpfxsoftclip_t * sc)

    extern const lpfxsoftclip_factory_t LPSoftClip

ctypedef void (*svf_filter_t)(SVFData* data)

ctypedef struct SVFData:
    double[4] Az 
    double[2] Bz
    double[3] Cz
    double[2] X

    double[3] M
    double freq
    double res
    double gain
    double shelf

ctypedef double (*HBAPProcess)(HBAP* data, double sample)

ctypedef struct HBAP:
    double d1
    double d2
    double d3
    double a0
    double a1	
    HBAPProcess process


cpdef SoundBuffer hpf(SoundBuffer snd, object freq=*, object res=*, bint norm=*)
cpdef SoundBuffer lpf(SoundBuffer snd, object freq=*, object res=*, bint norm=*)
cpdef SoundBuffer bpf(SoundBuffer snd, object freq=*, object res=*, bint norm=*)
cpdef SoundBuffer notchf(SoundBuffer snd, object freq=*, object res=*, bint norm=*)
cpdef SoundBuffer peakf(SoundBuffer snd, object freq=*, object res=*, bint norm=*)
cpdef SoundBuffer belleq(SoundBuffer snd, object freq=*, object q=*, object gain=*, bint norm=*)
cpdef SoundBuffer lshelfeq(SoundBuffer snd, object freq=*, object q=*, object gain=*, bint norm=*)
cpdef SoundBuffer hshelfeq(SoundBuffer snd, object freq=*, object q=*, object gain=*, bint norm=*)

cpdef SoundBuffer buttlpf(SoundBuffer snd, object freq)
cpdef SoundBuffer butthpf(SoundBuffer snd, object freq)
cpdef SoundBuffer buttbpf(SoundBuffer snd, object freq)
cpdef SoundBuffer buttbrf(SoundBuffer snd, object freq)

cpdef SoundBuffer mincer(SoundBuffer snd, double length, object position, object pitch, double amp=*, int wtsize=*)
cpdef SoundBuffer paulstretch(SoundBuffer snd, stretch=*, windowsize=*)
cpdef SoundBuffer saturator(SoundBuffer snd, double drive=*, double offset=*, bint dcblock=*)
cpdef SoundBuffer compressor(SoundBuffer snd, double ratio=*, double threshold=*, double attack=*, double release=*)
cpdef SoundBuffer crush(SoundBuffer snd, object bitdepth=*, object samplerate=*)

cpdef SoundBuffer norm(SoundBuffer snd, double ceiling)
cpdef SoundBuffer multifade(SoundBuffer buf, object pan=*, str method=*)
cpdef SoundBuffer diffuse(SoundBuffer buf, int channels=*, object pan=*, str method=*)
cpdef SoundBuffer fir(SoundBuffer snd, object impulse, bint normalize=*)
cpdef SoundBuffer fold(SoundBuffer snd, object amp=*, bint norm=*)
cpdef SoundBuffer envelope_follower(SoundBuffer snd, double window=*)
cpdef SoundBuffer widen(SoundBuffer snd, object width=*)
cpdef SoundBuffer softclip(SoundBuffer snd)
cpdef SoundBuffer softclip2(SoundBuffer snd)


