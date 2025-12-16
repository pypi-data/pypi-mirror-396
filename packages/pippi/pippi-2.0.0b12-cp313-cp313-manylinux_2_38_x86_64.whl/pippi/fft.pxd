#cython: language_level=3

from pippi.soundbuffer cimport (
    SoundBuffer, 
    lpbuffer_t, 
    lpfloat_t, 
    LPBuffer,
    LPWindow,
    LPInterpolation
)

cdef extern from "spectral.h":
    ctypedef struct lpspectral_factory_t:
        lpbuffer_t * (*convolve)(lpbuffer_t *, lpbuffer_t *)
        lpbuffer_t * (*process)(lpbuffer_t * snd, lpfloat_t length, lpbuffer_t * window, int (*callback)(lpfloat_t pos, lpbuffer_t * real, lpbuffer_t * imag), size_t blocksize)
    extern const lpspectral_factory_t LPSpectral

cpdef tuple to_xy(SoundBuffer mag, SoundBuffer arg)
cpdef tuple to_polar(SoundBuffer real, SoundBuffer imag)
cpdef SoundBuffer process(
        SoundBuffer snd, 
        double length=*, 
        object callback=*, 
        object window=*, 
        int blocksize=*
    )
