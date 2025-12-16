#cython: language_level=3

from pippi.soundbuffer cimport *

cdef extern from "oscs.shape.h":
    ctypedef struct lpshapeosc_t:
        lpbuffer_t * wt;
        lpfloat_t density;
        lpfloat_t periodicity;
        lpfloat_t stability;
        lpfloat_t phase;
        lpfloat_t freq;
        lpfloat_t minfreq;
        lpfloat_t maxfreq;
        lpfloat_t samplerate;

        lpfloat_t wtmin;
        lpfloat_t wtmax;
        lpfloat_t min;
        lpfloat_t max;

    ctypedef struct lpmultishapeosc_t:
        int numshapeosc;
        lpshapeosc_t ** shapeosc;
        lpfloat_t density;
        lpfloat_t periodicity;
        lpfloat_t stability;
        lpfloat_t minfreq;
        lpfloat_t maxfreq;
        lpfloat_t samplerate;
        lpfloat_t min;
        lpfloat_t max;

    ctypedef struct lpshapeosc_factory_t:
        lpshapeosc_t * (*create)(lpbuffer_t * wt);
        lpmultishapeosc_t * (*multi)(int numshapeosc, ...);
        lpfloat_t (*process)(lpshapeosc_t * s);
        lpfloat_t (*multiprocess)(lpmultishapeosc_t * m);
        void (*destroy)(lpshapeosc_t * s);
        void (*multidestroy)(lpmultishapeosc_t * m);

    extern const lpshapeosc_factory_t LPShapeOsc


#cpdef list onsets(double length, object density, object periodicity, object stability, double minfreq, double maxfreq)
cpdef SoundBuffer synth(object wt, double length=*, object density=*, object periodicity=*, object stability=*, double minfreq=*, double maxfreq=*, int samplerate=*, int channels=*)
#cdef double[:] _table(double[:] out, unsigned int length, double[:] wt, double[:] density, double[:] periodicity, double[:] stability, double[:] maxfreq, double[:] minfreq, int samplerate)
cpdef SoundBuffer win(object waveform, double lowvalue=*, double highvalue=*, double length=*, object density=*, object periodicity=*, object stability=*, object minfreq=*, object maxfreq=*, int samplerate=*)
cpdef SoundBuffer wt(object waveform, double lowvalue=*, double highvalue=*, double length=*, object density=*, object periodicity=*, object stability=*, object minfreq=*, object maxfreq=*, int samplerate=*)

