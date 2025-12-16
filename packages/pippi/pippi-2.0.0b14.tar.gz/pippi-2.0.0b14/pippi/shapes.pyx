#cython: language_level=3

from pippi.rand cimport rand, randint
from pippi.soundbuffer cimport SoundBuffer
from pippi cimport soundbuffer
from pippi.defaults cimport DEFAULT_SAMPLERATE, DEFAULT_CHANNELS

from libc cimport math

cimport numpy as np
import numpy as np

MIN_WT_FREQ = 0.3
MAX_WT_FREQ = 12

MIN_SYNTH_FREQ = 40
MAX_SYNTH_FREQ = 15000

cpdef SoundBuffer synth(
        object wt, 
        double length=1, 
        object density=0.5, 
        object periodicity=0.5, 
        object stability=0.5, 
        double minfreq=0, 
        double maxfreq=0, 
        int samplerate=DEFAULT_SAMPLERATE, 
        int channels=DEFAULT_CHANNELS
    ):

    if minfreq <= 0:
        minfreq = MIN_SYNTH_FREQ

    if maxfreq <= 0:
        maxfreq = MAX_SYNTH_FREQ

    cdef lpbuffer_t * _wt = soundbuffer.to_wavetable(wt)
    cdef lpbuffer_t * _density = soundbuffer.to_window(density)
    cdef lpbuffer_t * _periodicity = soundbuffer.to_window(periodicity)
    cdef lpbuffer_t * _stability = soundbuffer.to_window(stability)
    cdef lpbuffer_t * _minfreq = soundbuffer.to_window(minfreq)
    cdef lpbuffer_t * _maxfreq = soundbuffer.to_window(maxfreq)

    cdef size_t wt_length = _wt.length
    cdef size_t wt_boundry = max(wt_length-1, <size_t>1)
    cdef size_t framelength = <size_t>(length * samplerate)
    cdef lpbuffer_t * out = LPBuffer.create(framelength, channels, samplerate)

    cdef lpshapeosc_t * osc = LPShapeOsc.create(_wt)
    osc.samplerate = samplerate

    cdef size_t i=0
    cdef int c=0
    cdef double isamplerate = 1.0/samplerate
    cdef double pos=0, d=0, p=0, s=0, freq=1, phase=0, sample=0
    cdef double freqwidth = maxfreq - minfreq

    d = _density.data[0]
    p = 1 - _periodicity.data[0]
    freq = max((d * freqwidth) + minfreq + rand(freqwidth * -p, freqwidth * p), minfreq)

    for i in range(framelength):
        pos = <double>i / <double>length
        #sample = LPInterpolation.linear_point(_wt, phase)

        osc.density  = LPInterpolation.linear_pos(_density, pos)
        osc.periodicity  = LPInterpolation.linear_pos(_periodicity, pos)
        osc.stability  = LPInterpolation.linear_pos(_stability, pos)
        osc.minfreq  = LPInterpolation.linear_pos(_minfreq, pos)
        osc.maxfreq  = LPInterpolation.linear_pos(_maxfreq, pos)
        osc.freq = freq
        #out.data[i] = LPShapeOsc.process(osc)

        for c in range(channels):
            out.data[i * channels + c] = sample

        phase += isamplerate * wt_boundry * freq

        s = 1 - LPInterpolation.linear_pos(_stability, pos)
        s = math.log(s * (math.e-1) + 1)
        if phase >= wt_boundry and s > rand(0,1):
            d = LPInterpolation.linear_pos(_density, pos)
            p = 1 - LPInterpolation.linear_pos(_periodicity, pos)
            freq = max((d * freqwidth) + minfreq + rand(freqwidth * -p, freqwidth * p), minfreq)

        while phase >= wt_boundry:
            phase -= wt_boundry

    LPShapeOsc.destroy(osc)
    LPBuffer.destroy(_wt)
    LPBuffer.destroy(_density)
    LPBuffer.destroy(_periodicity)
    LPBuffer.destroy(_stability)
    LPBuffer.destroy(_minfreq)
    LPBuffer.destroy(_maxfreq)

    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer win(object waveform, double lowvalue=0, double highvalue=1, double length=1, object density=0.5, object periodicity=0.5, object stability=0.5, object minfreq=None, object maxfreq=None, int samplerate=DEFAULT_SAMPLERATE):
    if minfreq is None:
        minfreq = MIN_WT_FREQ

    if maxfreq is None:
        maxfreq = MAX_WT_FREQ

    cdef lpbuffer_t * _wt = soundbuffer.to_window(waveform)
    cdef lpbuffer_t * _density = soundbuffer.to_window(density)
    cdef lpbuffer_t * _periodicity = soundbuffer.to_window(periodicity)
    cdef lpbuffer_t * _stability = soundbuffer.to_window(stability)
    cdef lpbuffer_t * _minfreq = soundbuffer.to_window(minfreq)
    cdef lpbuffer_t * _maxfreq = soundbuffer.to_window(maxfreq)

    cdef size_t framelength = <size_t>(length * samplerate)

    cdef lpbuffer_t * out = LPBuffer.create(framelength, 1, samplerate)
    cdef lpshapeosc_t * osc = LPShapeOsc.create(_wt)
    osc.samplerate = samplerate
    cdef lpfloat_t pos = 0
    for i in range(framelength):
        pos = <lpfloat_t>i / framelength
        osc.density  = LPInterpolation.linear_pos(_density, pos)
        osc.periodicity  = LPInterpolation.linear_pos(_periodicity, pos)
        osc.stability  = LPInterpolation.linear_pos(_stability, pos)
        osc.minfreq  = LPInterpolation.linear_pos(_minfreq, pos)
        osc.maxfreq  = LPInterpolation.linear_pos(_maxfreq, pos)
        out.data[i] = LPShapeOsc.process(osc)

    LPShapeOsc.destroy(osc)
    LPBuffer.destroy(_wt)
    LPBuffer.destroy(_density)
    LPBuffer.destroy(_periodicity)
    LPBuffer.destroy(_stability)
    LPBuffer.destroy(_minfreq)
    LPBuffer.destroy(_maxfreq)

    if lowvalue != 0 or highvalue != 1:
        LPBuffer.scale(out, 0, 1, lowvalue, highvalue)

    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer wt(object waveform, double lowvalue=-1, double highvalue=1, double length=1, object density=0.5, object periodicity=0.5, object stability=0.5, object minfreq=None, object maxfreq=None, int samplerate=DEFAULT_SAMPLERATE):
    if minfreq is None:
        minfreq = MIN_WT_FREQ

    if maxfreq is None:
        maxfreq = MAX_WT_FREQ

    cdef lpbuffer_t * _wt = soundbuffer.to_wavetable(waveform)
    cdef lpbuffer_t * _density = soundbuffer.to_window(density)
    cdef lpbuffer_t * _periodicity = soundbuffer.to_window(periodicity)
    cdef lpbuffer_t * _stability = soundbuffer.to_window(stability)
    cdef lpbuffer_t * _minfreq = soundbuffer.to_window(minfreq)
    cdef lpbuffer_t * _maxfreq = soundbuffer.to_window(maxfreq)

    cdef size_t framelength = <size_t>(length * samplerate)
    cdef lpbuffer_t * out = LPBuffer.create(framelength, 1, samplerate)

    cdef lpshapeosc_t * osc = LPShapeOsc.create(_wt)
    osc.samplerate = samplerate
    cdef lpfloat_t pos = 0
    for i in range(framelength):
        pos = <lpfloat_t>i / framelength
        osc.density  = LPInterpolation.linear_pos(_density, pos)
        osc.periodicity  = LPInterpolation.linear_pos(_periodicity, pos)
        osc.stability  = LPInterpolation.linear_pos(_stability, pos)
        osc.minfreq  = LPInterpolation.linear_pos(_minfreq, pos)
        osc.maxfreq  = LPInterpolation.linear_pos(_maxfreq, pos)
        out.data[i] = LPShapeOsc.process(osc)

    LPShapeOsc.destroy(osc)
    LPBuffer.destroy(_wt)
    LPBuffer.destroy(_density)
    LPBuffer.destroy(_periodicity)
    LPBuffer.destroy(_stability)
    LPBuffer.destroy(_minfreq)
    LPBuffer.destroy(_maxfreq)

    if lowvalue != -1 or highvalue != 1:
        LPBuffer.scale(out, -1, 1, lowvalue, highvalue)

    return SoundBuffer._fromlpbuffer(out)

