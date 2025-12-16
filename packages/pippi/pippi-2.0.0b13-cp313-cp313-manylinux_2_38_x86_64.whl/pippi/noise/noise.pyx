#cython: language_level=3

from pippi.defaults cimport DEFAULT_CHANNELS, DEFAULT_SAMPLERATE
from pippi.soundbuffer cimport SoundBuffer, LPInterpolation, to_wavetable, to_window

cpdef SoundBuffer bln(object wt, double length, object minfreq, object maxfreq, int channels=DEFAULT_CHANNELS, int samplerate=DEFAULT_SAMPLERATE):
    cdef lpbuffer_t * _minfreq = to_window(minfreq)
    cdef lpbuffer_t * _maxfreq = to_window(maxfreq)
    cdef SoundBuffer out
    cdef Py_ssize_t i, c, framelength
    cdef lpbuffer_t * _wt
    cdef lpblnosc_t * osc
    cdef lpfloat_t sample
    cdef double pos = 0

    _wt = to_wavetable(wt)

    out = SoundBuffer(length=length, channels=channels, samplerate=samplerate)

    osc = LPBLNOsc.create(_wt, _minfreq.data[0], _maxfreq.data[0]);
    osc.samplerate = samplerate

    framelength = <Py_ssize_t>(length * samplerate)

    for i in range(framelength):
        pos = <double>i / <double>framelength
        osc.minfreq = <lpfloat_t>LPInterpolation.linear_pos(_minfreq, pos)
        osc.maxfreq = <lpfloat_t>LPInterpolation.linear_pos(_maxfreq, pos)

        sample = LPBLNOsc.process(osc)
        for c in range(<Py_ssize_t>channels):
            out.frames[i, c] = sample

    LPBLNOsc.destroy(osc);
    LPBuffer.destroy(_wt);
    LPBuffer.destroy(_minfreq);
    LPBuffer.destroy(_maxfreq);

    return out

