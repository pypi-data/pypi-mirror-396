#cython: language_level=3

import numbers
import math

cimport cython
import numpy as np
cimport numpy as np

from libc cimport math

from pippi.soundbuffer cimport (
    SoundBuffer,
    lpzapgremlins,
    to_window,
    to_wavetable,
    LPBuffer,
    LPFX,
    LPInterpolation,
    lpbuffer_t,
    lpfloat_t
)

from pippi cimport soundbuffer
from pippi.dsp cimport _mag
from pippi.defaults cimport PI
from pippi cimport rand
#from pippi cimport soundpipe
from cpython cimport bool
from libc.stdlib cimport malloc, free


cdef double MINDENSITY = 0.001


cdef double ** memoryview2ftbls(double[:,:] snd):
    cdef int length = snd.shape[0]
    cdef int channels = snd.shape[1]
    cdef int i = 0
    cdef int c = 0
    cdef double** tbls = <double**>malloc(channels * sizeof(double*))
    cdef double* tbl

    for c in range(channels):
        tbl = <double*>malloc(length * sizeof(double))
        for i in range(length):
            tbl[i] = <double>snd[i,c]
        tbls[c] = tbl

    return tbls

cpdef SoundBuffer buttlpf(SoundBuffer snd, object freq):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef lpfloat_t sample=0, output=0
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0
    cdef lpbfilter_t * f
    cdef lpbalance_t * bal

    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    cdef lpbuffer_t * _freq = to_window(freq)

    for c in range(channels):
        f = LPFilter.create_blp(_freq.data[0], snd.samplerate)
        bal = LPFX.create_balancer(snd.samplerate)

        for i in range(length):
            pos = <double>i / <double>length
            f.freq = LPInterpolation.linear_pos(_freq, pos)
            if channels == 1:
                sample = snd[i]
            else:
                sample = snd[i][c]
            output = LPFilter.process_blp(f, sample)
            out.data[i * channels + c] = LPFX.balance(bal, output, sample)

        LPFX.destroy_balancer(bal)
        LPMemoryPool.free(f)

    LPBuffer.destroy(_freq)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer buttlpf_soundpipe(SoundBuffer snd, object freq):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef sp_data * sp
    cdef sp_butlp * butlp
    cdef sp_bal * bal
    cdef double sample = 0
    cdef double filtered = 0
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0

    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    cdef lpbuffer_t * _freq = to_window(freq)

    sp_create(&sp)

    for c in range(channels):
        sp_bal_create(&bal)
        sp_bal_init(sp, bal)
        sp_butlp_create(&butlp)
        sp_butlp_init(sp, butlp)

        for i in range(length):
            pos = <double>i / <double>length
            butlp.freq = LPInterpolation.linear_pos(_freq, pos)
            if channels == 1:
                sample = snd[i]
            else:
                sample = snd[i][c]
            sp_butlp_compute(sp, butlp, &sample, &filtered)
            sp_bal_compute(sp, bal, &filtered, &sample, &output)
            out.data[i * channels + c] = <double>output

        sp_butlp_destroy(&butlp)
        sp_bal_destroy(&bal)

    sp_destroy(&sp)

    LPBuffer.destroy(_freq)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer butthpf(SoundBuffer snd, object freq):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef sp_data * sp
    cdef sp_buthp * buthp
    cdef sp_bal * bal 
    cdef double sample = 0
    cdef double filtered = 0
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0

    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    cdef lpbuffer_t * _freq = to_window(freq)

    sp_create(&sp)

    for c in range(channels):
        sp_bal_create(&bal)
        sp_bal_init(sp, bal)
        sp_buthp_create(&buthp)
        sp_buthp_init(sp, buthp)

        for i in range(length):
            pos = <double>i / <double>length
            buthp.freq = LPInterpolation.linear_pos(_freq, pos)
            if channels == 1:
                sample = snd[i]
            else:
                sample = snd[i][c]
            sp_buthp_compute(sp, buthp, &sample, &filtered)
            sp_bal_compute(sp, bal, &filtered, &sample, &output)
            out.data[i * channels + c] = <double>output

        sp_buthp_destroy(&buthp)
        sp_bal_destroy(&bal)

    sp_destroy(&sp)

    LPBuffer.destroy(_freq)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer buttbpf(SoundBuffer snd, object freq):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef sp_data * sp
    cdef sp_butbp * butbp
    cdef sp_bal * bal 
    cdef double sample = 0
    cdef double filtered = 0
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0

    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    cdef lpbuffer_t * _freq = to_window(freq)

    sp_create(&sp)

    for c in range(channels):
        sp_bal_create(&bal)
        sp_bal_init(sp, bal)
        sp_butbp_create(&butbp)
        sp_butbp_init(sp, butbp)

        for i in range(length):
            pos = <double>i / <double>length
            butbp.freq = LPInterpolation.linear_pos(_freq, pos)
            if channels == 1:
                sample = snd[i]
            else:
                sample = snd[i][c]
            sp_butbp_compute(sp, butbp, &sample, &filtered)
            sp_bal_compute(sp, bal, &filtered, &sample, &output)
            out.data[i * channels + c] = <double>output

        sp_butbp_destroy(&butbp)
        sp_bal_destroy(&bal)

    sp_destroy(&sp)

    LPBuffer.destroy(_freq)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer buttbrf(SoundBuffer snd, object freq):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef sp_data * sp
    cdef sp_butbr * butbr
    cdef sp_bal * bal 
    cdef double sample = 0
    cdef double filtered = 0
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0

    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    cdef lpbuffer_t * _freq = to_window(freq)

    sp_create(&sp)

    for c in range(channels):
        sp_bal_create(&bal)
        sp_bal_init(sp, bal)
        sp_butbr_create(&butbr)
        sp_butbr_init(sp, butbr)

        for i in range(length):
            pos = <double>i / <double>length
            butbr.freq = LPInterpolation.linear_pos(_freq, pos)
            if channels == 1:
                sample = snd[i]
            else:
                sample = snd[i][c]
            sp_butbr_compute(sp, butbr, &sample, &filtered)
            sp_bal_compute(sp, bal, &filtered, &sample, &output)
            out.data[i * channels + c] = <double>output

        sp_butbr_destroy(&butbr)
        sp_bal_destroy(&bal)

    sp_destroy(&sp)

    LPBuffer.destroy(_freq)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer mincer(SoundBuffer snd, double length, object position, object pitch, double amp=1, int wtsize=4096):
    cdef size_t snd_length = snd.length
    cdef int channels = snd.channels
    cdef int samplerate = snd.samplerate
    cdef sp_data * sp
    cdef sp_mincer * mincer
    cdef sp_ftbl * tbl
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0
    cdef double sourcelength = <double>snd_length / <double>samplerate
    cdef size_t out_length = <size_t>(samplerate * length)
    
    cdef lpbuffer_t * out = LPBuffer.create(out_length, channels, samplerate)
    cdef lpbuffer_t * time_lfo = to_window(position)
    cdef lpbuffer_t * pitch_lfo = to_window(pitch)
    cdef double[:,:] frames = snd.frames
    cdef double** tbls = memoryview2ftbls(frames)
    
    sp_create(&sp)
    
    for c in range(channels):
        sp_ftbl_bind(sp, &tbl, tbls[c], snd_length)
        sp_mincer_create(&mincer)
        sp_mincer_init(sp, mincer, tbl, wtsize)
        
        mincer.amp = amp
        
        for i in range(out_length):
            pos = <double>i / <double>out_length
            mincer.time = LPInterpolation.linear_pos(time_lfo, pos) * sourcelength
            mincer.pitch = LPInterpolation.linear_pos(pitch_lfo, pos)
            sp_mincer_compute(sp, mincer, NULL, &output)
            out.data[i * channels + c] = <double>output
            
        sp_mincer_destroy(&mincer)
        sp_ftbl_destroy(&tbl)
        free(tbls[c])
        
    sp_destroy(&sp)
    free(tbls)

    LPBuffer.destroy(time_lfo)
    LPBuffer.destroy(pitch_lfo)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer paulstretch(SoundBuffer snd, stretch=1, windowsize=1):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef int samplerate = snd.samplerate
    cdef size_t outlength = <size_t>(stretch * samplerate)
    cdef sp_data * sp
    cdef sp_paulstretch * paulstretch
    cdef sp_ftbl * tbl
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    cdef double[:,:] frames = snd.frames
    cdef double** tbls = memoryview2ftbls(frames)
    
    cdef lpbuffer_t * out = LPBuffer.create(outlength, channels, samplerate)
    
    sp_create(&sp)
    
    for c in range(channels):
        sp_ftbl_bind(sp, &tbl, tbls[c], length)
        sp_paulstretch_create(&paulstretch)
        sp_paulstretch_init(sp, paulstretch, tbl, windowsize, stretch)
        
        for i in range(outlength):
            sp_paulstretch_compute(sp, paulstretch, NULL, &output)
            out.data[i * channels + c] = <double>output
            
        sp_paulstretch_destroy(&paulstretch)
        sp_ftbl_destroy(&tbl)
        free(tbls[c])
        
    sp_destroy(&sp)
    free(tbls)
    
    return snd.fromlpbuffer(out)

cpdef SoundBuffer saturator(SoundBuffer snd, double drive=10, double offset=0, bint dcblock=True):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef sp_data * sp
    cdef sp_saturator * saturator
    cdef sp_dcblock * dcblocker
    cdef double sample = 0
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    
    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    
    sp_create(&sp)
    
    for c in range(channels):
        sp_saturator_create(&saturator)
        sp_saturator_init(sp, saturator)
        
        saturator.drive = drive
        saturator.dcoffset = offset
        
        if dcblock:
            sp_dcblock_create(&dcblocker)
            sp_dcblock_init(sp, dcblocker)
        
        for i in range(length):
            if channels == 1:
                sample = snd[i]
            else:
                sample = snd[i][c]
            sp_saturator_compute(sp, saturator, &sample, &output)
            if dcblock:
                sp_dcblock_compute(sp, dcblocker, &output, &output)
            out.data[i * channels + c] = <double>output
            
        sp_saturator_destroy(&saturator)
        if dcblock:
            sp_dcblock_destroy(&dcblocker)
            
    sp_destroy(&sp)
    
    return snd.fromlpbuffer(out)

cpdef SoundBuffer compressor(SoundBuffer snd, double ratio=4, double threshold=-30, double attack=0.2, double release=0.2):
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef sp_data * sp
    cdef sp_compressor * compressor
    cdef double sample = 0
    cdef double output = 0
    cdef size_t i = 0
    cdef int c = 0
    
    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    
    sp_create(&sp)
    
    for c in range(channels):
        sp_compressor_create(&compressor)
        sp_compressor_init(sp, compressor)
        
        compressor.ratio = &ratio
        compressor.thresh = &threshold
        compressor.atk = &attack
        compressor.rel = &release
        
        for i in range(length):
            if channels == 1:
                sample = snd[i]
            else:
                sample = snd[i][c]
            sp_compressor_compute(sp, compressor, &sample, &output)
            out.data[i * channels + c] = <double>output
            
        sp_compressor_destroy(&compressor)
        
    sp_destroy(&sp)
    
    return snd.fromlpbuffer(out)

cpdef SoundBuffer crush(SoundBuffer snd, object bitdepth=None, object samplerate=None):
    if bitdepth is None:
        bitdepth = rand.rand(0, 16)
    if samplerate is None:
        samplerate = rand.rand(0, snd.samplerate)
        
    cdef size_t length = snd.length
    cdef int channels = snd.channels
    cdef sp_data * sp
    cdef sp_bitcrush * bitcrush
    cdef double sample = 0
    cdef double crushed = 0
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0
    
    cdef lpbuffer_t * _bitdepth = to_window(bitdepth)
    cdef lpbuffer_t * _samplerate = to_window(samplerate)
    cdef lpbuffer_t * out = LPBuffer.create(length, channels, snd.samplerate)
    
    sp_create(&sp)
    
    for c in range(channels):
        sp_bitcrush_create(&bitcrush)
        sp_bitcrush_init(sp, bitcrush)
        
        for i in range(length):
            pos = <double>i / <double>length
            bitcrush.bitdepth = LPInterpolation.linear_pos(_bitdepth, pos)
            bitcrush.srate = LPInterpolation.linear_pos(_samplerate, pos)
            sample = snd.buffer.data[i * channels + c]
            sp_bitcrush_compute(sp, bitcrush, &sample, &crushed)
            out.data[i * channels + c] = crushed
            
        sp_bitcrush_destroy(&bitcrush)

    sp_destroy(&sp)

    LPBuffer.destroy(_bitdepth)
    LPBuffer.destroy(_samplerate)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer crossfade(SoundBuffer a, SoundBuffer b, object curve=None):
    if curve is None:
        curve = 'saw'
    cdef lpbuffer_t * _curve = to_window(curve)
    cdef lpbuffer_t * out = LPFX.crossfade(a.buffer, b.buffer, _curve)
    LPBuffer.destroy(_curve)
    return SoundBuffer._fromlpbuffer(out)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _distort(lpbuffer_t * snd, lpbuffer_t * out):
    """ Non-linear distortion ported from supercollider """
    cdef size_t i=0
    cdef int c=0
    cdef size_t framelength = snd.length
    cdef int channels = snd.channels
    cdef double s = 0

    for i in range(framelength):
        for c in range(channels):
            s = snd.data[i * channels + c]
            if s > 0:
                out.data[i * channels + c] = s / (1.0 + abs(s))
            else:
                out.data[i * channels + c] = s / (1.0 - s)

    return out

cpdef SoundBuffer distort(SoundBuffer snd):
    """ Non-linear distortion ported from supercollider """
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    out = _distort(snd.buffer, out)
    return snd.fromlpbuffer(out)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef double _blsc_integrated_clip(double val) nogil:
    cdef double out

    if val < -1:
        out = -4 / 5. * val - (1/3.0)
    else:
        out = (val * val) / 2.0 - val**6 / 30.0

    if val < 1:
        return out
    else:
        return 4./5.0 * val - 1./3.0

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _softclip(lpbuffer_t * out, lpbuffer_t * snd) noexcept nogil:
    cdef double val=0, lastval=0, sample=0
    cdef int c=0
    cdef size_t i=0
    cdef int channels = snd.channels
    cdef size_t length = snd.length

    for c in range(channels):
        lastval = 0
        for i in range(length):
            val = snd.data[i * channels + c]
            if abs(val - lastval) == 0.0:
                sample = (val + lastval)/2.0

                if sample < -1:
                    sample = -4. / 5.
                else:
                    sample = sample - sample**5 / 5.
                
                if sample >= 1:
                    sample = 4. / 5.

            else:
                sample = (_blsc_integrated_clip(val) - _blsc_integrated_clip(lastval)) / (val - lastval)

            out.data[i * channels + c] = sample
            lastval = val

    return out

cpdef SoundBuffer softclip(SoundBuffer snd):
    """ Zener diode clipping simulation implemented by Liquid City Motors Will Mitchell
    """
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    out = _softclip(out, snd.buffer)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer softclip2(SoundBuffer snd):
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef lpfxsoftclip_t * clipper
    cdef size_t i
    cdef int c

    for c in range(snd.channels):
        clipper = LPSoftClip.create()
        for i in range(snd.buffer.length):
            out.data[i * snd.channels + c] = LPSoftClip.process(clipper, snd[i,c])
        LPSoftClip.destroy(clipper)

    return snd.fromlpbuffer(out)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _crossover(lpbuffer_t * snd, lpbuffer_t * amount, lpbuffer_t * smooth, lpbuffer_t * fade):
    """ Crossover distortion ported from the supercollider CrossoverDistortion ugen """
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef size_t i=0, framelength=snd.length
    cdef int c=0, channels=snd.channels
    cdef double s=0, pos=0, a=0, f=0, m=0

    for i in range(framelength):
        pos = <double>i / <double>framelength
        a = LPInterpolation.linear_pos(amount, pos)
        m = LPInterpolation.linear_pos(smooth, pos)
        f = LPInterpolation.linear_pos(fade, pos)

        for c in range(channels):
            out.data[i * channels + c] = LPFX.crossover(snd.data[i * channels + c], a, m, f)

    return out

cpdef SoundBuffer crossover(SoundBuffer snd, object amount, object smooth, object fade):
    """ Crossover distortion ported from the supercollider CrossoverDistortion ugen """
    cdef lpbuffer_t * _amount = to_window(amount)
    cdef lpbuffer_t * _smooth = to_window(smooth)
    cdef lpbuffer_t * _fade = to_window(fade)
    cdef lpbuffer_t * out = _crossover(snd.buffer, _amount, _smooth, _fade)
    LPBuffer.destroy(_amount)
    LPBuffer.destroy(_smooth)
    LPBuffer.destroy(_fade)
    return snd.fromlpbuffer(out)

cdef double _fold_point(double sample, double last, double samplerate):
    # Adapted from https://ccrma.stanford.edu/~jatin/ComplexNonlinearities/Wavefolder.html
    cdef double z = math.tanh(sample) + (math.tanh(last) * 0.9)
    return z + (-0.5 * math.sin(2 * PI * sample * (samplerate/2) / samplerate))

cdef lpbuffer_t * _fold(lpbuffer_t * snd, lpbuffer_t * amp, double samplerate):
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef double last=0, sample=0, pos=0
    cdef size_t length = snd.length
    cdef size_t i = 0
    cdef int c = 0
    cdef int channels = snd.channels

    for c in range(channels):
        last = 0
        for i in range(length):
            pos = <double>i / length
            sample = snd.data[i * channels + c] * LPInterpolation.linear_pos(amp, pos)
            sample = _fold_point(sample, last, samplerate)
            last = sample
            out.data[i * channels + c] = lpzapgremlins(sample)

    return out

cpdef SoundBuffer fold(SoundBuffer snd, object amp=1, bint norm=True):
    cdef lpbuffer_t * _amp = to_window(amp)
    out = _fold(snd.buffer, _amp, <double>snd.samplerate)
    LPBuffer.destroy(_amp)
    if norm:
        LPFX.norm(out, snd.mag)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer norm(SoundBuffer snd, double ceiling):
    LPFX.norm(snd.buffer, ceiling)
    return snd

cpdef SoundBuffer multifade(SoundBuffer buf, object pan=0.5, str method=None):
    """ Crossfade across multiple channels based on pan position.

    This takes a multichannel buffer and collapses it to mono by crossfading
    between channels based on the pan value, which can modulate over time.

    Args:
        buf: multichannel SoundBuffer to process
        pan: pan position from 0 (first channel) to 1 (last channel)
             Can be a float, list, or SoundBuffer for modulation over time
        method: 'constant' for constant power (default), 'linear' for linear crossfade

    Returns:
        Mono SoundBuffer with crossfaded samples

    Examples:
        >>> # Collapse 3-channel buffer to mono, panned to center
        >>> mono = multifade(three_ch_buf, pan=0.5)
        >>>
        >>> # Modulate pan over time with an LFO
        >>> lfo = SoundBuffer.win('sine', length=buf.dur)
        >>> mono = multifade(three_ch_buf, pan=lfo)
    """
    if method is None:
        method = 'constant'

    cdef int _method = soundbuffer.PANMETHOD_CONSTANT if method == 'constant' else soundbuffer.PANMETHOD_LINEAR
    cdef lpbuffer_t * _pan = to_window(pan, len(buf))
    cdef lpbuffer_t * out = LPBuffer.create(buf.buffer.length, 1, buf.buffer.samplerate)
    cdef size_t i
    cdef lpfloat_t pos, pan_value

    for i in range(buf.buffer.length):
        pos = <lpfloat_t>i / buf.buffer.length
        pan_value = LPInterpolation.linear_pos(_pan, pos)
        out.data[i] = LPFX.multifade(buf.buffer, pos, pan_value, _method)

    LPBuffer.destroy(_pan)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer diffuse(SoundBuffer buf, int channels=2, object pan=0.5, str method=None):
    """ Diffuse a mono buffer across multiple output channels.

    This takes a mono (or multichannel) buffer and positions it within
    a multichannel output space based on the pan value, which can modulate
    over time.

    Args:
        buf: SoundBuffer to diffuse (will be mixed to mono if multichannel)
        channels: number of output channels (default: 2)
        pan: pan position from 0 (first channel) to 1 (last channel)
             Can be a float, list, or SoundBuffer for modulation over time
        method: 'constant' for constant power (default), 'linear' for linear

    Returns:
        Multichannel SoundBuffer with diffused samples

    Examples:
        >>> # Diffuse mono sound across 3 channels, panned to center
        >>> three_ch = diffuse(mono, channels=3, pan=0.5)
        >>>
        >>> # Modulate pan over time with an LFO
        >>> lfo = SoundBuffer.win('sine', length=mono.dur)
        >>> moving = diffuse(mono, channels=4, pan=lfo)
    """
    if method is None:
        method = 'constant'

    # Mix to mono if needed
    cdef SoundBuffer mono_buf = buf if buf.channels == 1 else buf.remix(1)

    cdef int _method = soundbuffer.PANMETHOD_CONSTANT if method == 'constant' else soundbuffer.PANMETHOD_LINEAR
    cdef lpbuffer_t * _pan = to_window(pan, len(mono_buf))
    cdef lpbuffer_t * out = LPBuffer.create(mono_buf.buffer.length, channels, mono_buf.buffer.samplerate)
    cdef size_t i
    cdef lpfloat_t pos, pan_value, sample

    for i in range(mono_buf.buffer.length):
        pos = <lpfloat_t>i / mono_buf.buffer.length
        pan_value = LPInterpolation.linear_pos(_pan, pos)
        sample = mono_buf.buffer.data[i]
        LPFX.diffuse(out, i, sample, pan_value, _method)

    LPBuffer.destroy(_pan)
    return SoundBuffer._fromlpbuffer(out)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _vspeed(lpbuffer_t * snd, lpbuffer_t * chan, lpbuffer_t * out, lpbuffer_t * lfo, double minspeed, double maxspeed, int samplerate):
    cdef size_t i = 0
    cdef int c = 0
    cdef size_t framelength = snd.length
    cdef int channels = snd.channels
    cdef double speed = 0
    cdef double posinc = 1.0 / <double>framelength
    cdef double pos = 0
    cdef double lfopos = 0

    for c in range(channels):
        for i in range(framelength):
            chan.data[i] = snd.data[i * channels + c]

        pos = 0
        lfopos = 0
        for i in range(framelength):
            speed = LPInterpolation.linear(lfo, lfopos) * (maxspeed - minspeed) + minspeed
            out.data[i * channels + c] = LPInterpolation.linear(chan, pos)
            pos += posinc * speed
            lfopos += posinc

    return out

cpdef SoundBuffer vspeed(SoundBuffer snd, object lfo, double minspeed, double maxspeed):
    cdef lpbuffer_t * _lfo = to_wavetable(lfo)
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef lpbuffer_t * chan = LPBuffer.create(snd.length, 1, snd.samplerate)
    out = _vspeed(snd.buffer, chan, out, _lfo, minspeed, maxspeed, snd.samplerate)
    LPBuffer.destroy(_lfo)
    LPBuffer.destroy(chan)
    return SoundBuffer._fromlpbuffer(out)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _widen(lpbuffer_t * snd, lpbuffer_t * out, lpbuffer_t * width):
    cdef double mid, w, pos
    cdef int channels = snd.channels
    cdef size_t length = snd.length
    cdef size_t i = 0;
    cdef int c, d=0

    for i in range(length-1):
        pos = <double>i / length
        w = LPInterpolation.linear_pos(width, pos)
        mid = (1.0-w) / (1.0 + w)
        for c in range(channels):
            d = c + 1
            while d > channels:
                d -= channels
            out.data[i * channels + c] = snd.data[(i+1) * channels + c] + mid * snd.data[(i+1) * channels + d]

    return out

cpdef SoundBuffer widen(SoundBuffer snd, object width=1):
    cdef lpbuffer_t * _width = to_window(width)
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    out = _widen(snd.buffer, out, _width)
    LPBuffer.destroy(_width)
    return SoundBuffer._fromlpbuffer(out)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _delay(lpbuffer_t * snd, lpbuffer_t * out, int delayframes, double feedback):
    cdef size_t i = 0
    cdef int c = 0
    cdef size_t framelength = snd.length
    cdef int channels = snd.channels
    cdef int delayindex = 0
    cdef double sample = 0

    for i in range(framelength):
        delayindex = i - delayframes
        for c in range(channels):
            if delayindex < 0:
                sample = snd.data[i * channels + c]
            else:
                sample = snd.data[delayindex * channels + c] * feedback
                snd.data[i * channels + c] += sample
            out.data[i * channels + c] = sample

    return out

cpdef SoundBuffer delay(SoundBuffer snd, double delaytime, double feedback):
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef int delayframes = <int>(snd.samplerate * delaytime)
    out = _delay(snd.buffer, out, delayframes, feedback)
    return snd.fromlpbuffer(out)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(False)
cdef lpbuffer_t * _vdelay(lpbuffer_t * snd, 
                         lpbuffer_t * out, 
                         lpbuffer_t * lfo, 
                         double[:,:] delayline, 
                         double mindelay, 
                         double maxdelay, 
                         double feedback, 
                         int samplerate):
    cdef size_t i = 0
    cdef int c = 0
    cdef double pos = 0
    cdef size_t framelength = snd.length
    cdef int delaylinelength = len(delayline)
    cdef int channels = snd.channels
    cdef int delayindex = 0
    cdef int delayindexnext = 0
    cdef int delaylineindex = 0
    cdef double sample = 0
    cdef double output = 0
    cdef double delaytime = 0
    cdef int delayframes = 0

    delayindex = 0

    for i in range(framelength):
        pos = <double>i / <double>framelength
        delaytime = (LPInterpolation.linear_pos(lfo, pos) * (maxdelay-mindelay) + mindelay) * samplerate
        delayreadindex = <int>(i - delaytime)
        for c in range(channels):
            sample = snd.data[i * channels + c]

            if delayreadindex >= 0:
                output = snd.data[delayreadindex * channels + c] * feedback
                sample += output

            delayindex += 1
            delayindex %= delaylinelength

            delayline[delayindex,c] = output

            out.data[i * channels + c] = sample

    return out

cpdef SoundBuffer vdelay(SoundBuffer snd, object lfo, double mindelay, double maxdelay, double feedback):
    cdef lpbuffer_t * lfo_wt = to_wavetable(lfo, 4096)
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef int maxdelayframes = <int>(snd.samplerate * maxdelay)
    cdef double[:,:] delayline = np.zeros((maxdelayframes, snd.channels), dtype='d')
    out = _vdelay(snd.buffer, out, lfo_wt, delayline, mindelay, maxdelay, feedback, snd.samplerate)
    LPBuffer.destroy(lfo_wt)
    return snd.fromlpbuffer(out)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _mdelay(lpbuffer_t * snd, lpbuffer_t * out, int[:] delays, double feedback):
    cdef size_t i = 0
    cdef int c = 0
    cdef int j = 0
    cdef size_t framelength = snd.length
    cdef int numdelays = len(delays)
    cdef int channels = snd.channels
    cdef int delayindex = 0
    cdef double sample = 0
    cdef double dsample = 0
    cdef double output = 0
    cdef int delaylinestart = 0
    cdef int delaylinepos = 0
    cdef int delayreadindex = 0

    cdef int delaylineslength = sum(delays)
    cdef double[:,:] delaylines = np.zeros((delaylineslength, channels), dtype='d')
    cdef int[:] delaylineindexes = np.zeros(numdelays, dtype='i')

    for i in range(framelength):
        for c in range(channels):
            sample = snd.data[i * channels + c]
            delaylinestart = 0
            for j in range(numdelays):
                delayreadindex = i - delays[j]
                delayindex = delaylineindexes[j]
                delaylinepos = delaylinestart + delayindex
                output = delaylines[delaylinepos,c]

                if delayreadindex < 0:
                    dsample = 0
                else:
                    dsample = snd.data[delayreadindex * channels + c] * feedback
                    output += dsample
                    sample += output

                delayindex += 1
                delayindex %= delays[j]

                delaylines[delaylinepos,c] = output
                delaylineindexes[j] = delayindex
                delaylinestart += delays[j]

            out.data[i * channels + c] = sample

    return out

cpdef SoundBuffer mdelay(SoundBuffer snd, list delays, double feedback):
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef int numdelays = len(delays)
    cdef double delay
    cdef int[:] delayframes = np.array([ snd.samplerate * delay for delay in delays ], dtype='i')
    out = _mdelay(snd.buffer, out, delayframes, feedback)
    return snd.fromlpbuffer(out)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef lpbuffer_t * _fir(lpbuffer_t * snd, lpbuffer_t * out, lpbuffer_t * impulse, bint norm=True):
    cdef size_t i=0, j=0
    cdef int c=0
    cdef size_t framelength = snd.length
    cdef int channels = snd.channels
    cdef size_t impulselength = impulse.length
    cdef double maxval = 0     

    if norm:
        maxval = LPBuffer.mag(snd)

    for i in range(framelength):
        for c in range(channels):
            for j in range(impulselength):
                out.data[(i+j) * channels + c] += snd.data[i * channels + c] * impulse.data[j]

    if norm:
        LPFX.norm(out, maxval)

    return out

cpdef SoundBuffer fir(SoundBuffer snd, object impulse, bint normalize=True):
    cdef lpbuffer_t * impulsewt = to_window(impulse)
    cdef lpbuffer_t * out = LPBuffer.create(snd.length+impulsewt.length-1, snd.channels, snd.samplerate)
    out = _fir(snd.buffer, out, impulsewt, normalize)
    LPBuffer.destroy(impulsewt)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer envelope_follower(SoundBuffer snd, double window=0.015):
    cdef int blocksize = <int>(window * snd.samplerate)
    cdef size_t length = len(snd)
    cdef size_t barrier = length - blocksize
    cdef SoundBuffer flat = snd.remix(1)
    cdef double val = 0
    cdef size_t i = 0
    cdef int j, ei = 0
    cdef int numblocks = <int>(length / blocksize)
    cdef double[:] env = np.zeros(numblocks, dtype='d')
    cdef lpbuffer_t * out = LPBuffer.create(numblocks, 1, snd.samplerate)

    while i < barrier:
        val = 0
        for j in range(blocksize):
            val = max(val, abs(flat[i+j]))

        env[ei] = val

        i += blocksize
        ei += 1

    return snd.fromlpbuffer(out)

cpdef SoundBuffer convolve(SoundBuffer snd, SoundBuffer impulse, bint norm=True):
    cdef lpbuffer_t * out = LPSpectral.convolve(snd.buffer, impulse.buffer)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer tconvolve(SoundBuffer snd, object impulse, bool normalize=True):
    cdef lpbuffer_t * imp = soundbuffer.to_window(impulse)
    cdef lpbuffer_t * out = LPBuffer.create(snd.length +  imp.length + 1, snd.channels, snd.samplerate)
    LPFX.convolve(snd.buffer, imp, out)
    LPBuffer.destroy(imp)
    return snd.fromlpbuffer(out)

"""
cpdef SoundBuffer go(SoundBuffer snd, 
                          object factor,
                          double density=1, 
                          double wet=1,
                          double minlength=0.01, 
                          double maxlength=0.06, 
                          double minclip=0.4, 
                          double maxclip=0.8, 
                          object win=None
                    ):
    if wet <= 0:
        return snd

    cdef wavetables.Wavetable factors = None
    if not isinstance(factor, numbers.Real):
        factors = wavetables.Wavetable(factor)

    density = max(MINDENSITY, density)

    cdef double outlen = snd.dur + maxlength
    cdef SoundBuffer out = SoundBuffer(length=outlen, channels=snd.channels, samplerate=snd.samplerate)
    cdef wavetables.Wavetable window
    if win is None:
        window = wavetables.Wavetable(wavetables.HANN)
    else:
        window = wavetables.Wavetable(win)

    cdef double grainlength = rand.rand(minlength, maxlength)
    cdef double pos = 0
    cdef double clip
    cdef SoundBuffer grain

    while pos < outlen:
        grain = snd.cut(pos, grainlength)
        grain *= rand.rand(0, factor * wet)
        grain = grain.softclip()
        out.dub(grain * window.data, pos)

        pos += (grainlength/2) * (1/density)
        grainlength = rand.rand(minlength, maxlength)

    if wet > 0:
        out *= wet

    if wet < 1:
        out.dub(snd * abs(wet-1), 0)

    return out
"""

# Wrappers for libpippi port of Liquid City Motors Will's SVF
cdef lpbuffer_t * _svf_process(int mode, lpbuffer_t * snd, object freq, object res_or_q, object gain):
    cdef lpbuffer_t * out = LPBuffer.create(snd.length, snd.channels, snd.samplerate)
    cdef lpsvf_t * svf
    cdef int c = 0
    cdef size_t i = 0
    cdef lpfloat_t sample = 0, pos = 0

    cdef lpbuffer_t * _freq = to_window(freq)
    cdef lpbuffer_t * _res_or_q = to_window(res_or_q)
    cdef lpbuffer_t * _gain = to_window(gain)

    for c in range(snd.channels):
        svf = LPFilter.create_svf(mode)
        for i in range(snd.length):
            pos = <lpfloat_t>i / snd.length
            if _gain != NULL:
                svf.gain = LPInterpolation.linear_pos(_gain, pos)
            svf.freq = max(min(LPInterpolation.linear_pos(_freq, pos) / snd.samplerate, 0.49), -.49)
            if _res_or_q != NULL:
                svf.res = LPInterpolation.linear_pos(_res_or_q, pos)
            sample = LPFilter.process_svf(svf, snd.data[i * snd.channels + c])
            out.data[i * snd.channels + c] = sample
        LPFilter.destroy_svf(svf)

    LPBuffer.destroy(_freq)
    LPBuffer.destroy(_res_or_q)
    LPBuffer.destroy(_gain)

    return out

cpdef SoundBuffer hpf(SoundBuffer snd, object freq=None, object res=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_HIGHPASS, snd.buffer, freq, res, None)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer lpf(SoundBuffer snd, object freq=None, object res=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_LOWPASS, snd.buffer, freq, res, None)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer bpf(SoundBuffer snd, object freq=None, object res=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_BANDPASS, snd.buffer, freq, res, None)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer notchf(SoundBuffer snd, object freq=None, object res=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_NOTCH, snd.buffer, freq, res, None)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer peakf(SoundBuffer snd, object freq=None, object res=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_PEAK, snd.buffer, freq, res, None)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer belleq(SoundBuffer snd, object freq=None, object q=None, object gain=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_BELL, snd.buffer, freq, q, gain)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer lshelfeq(SoundBuffer snd, object freq=None, object q=None, object gain=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_LOWSHELF, snd.buffer, freq, q, gain)
    return SoundBuffer._fromlpbuffer(out)

cpdef SoundBuffer hshelfeq(SoundBuffer snd, object freq=None, object q=None, object gain=None, bint norm=True):
    cdef lpbuffer_t * out = _svf_process(FILTER_HIGHSHELF, snd.buffer, freq, q, gain)
    return SoundBuffer._fromlpbuffer(out)

# mid/side encoding/decoding

cdef double _m_encode(double left, double right):
    return (left + right) * .707

cdef double _s_encode(double left, double right):
    return (left - right) * .707 

cdef double _l_decode(double mid, double side):
    return (mid + side) * .707

cdef double _r_decode(double mid, double side):
    return (mid - side) * .707

cpdef SoundBuffer ms_encode(SoundBuffer snd):
    snd = snd.remix(2)
    cdef int length = len(snd)
    cdef double[:,:] out = np.zeros((length, 2), dtype='d')
    cdef double[:,:] frames = snd.frames
    for i in range(length):
        out[i, 0] = _m_encode(snd.frames[i, 0], snd.frames[i, 1])
        out[i, 1] = _s_encode(snd.frames[i, 0], snd.frames[i, 1])
    return SoundBuffer(out, channels=2, samplerate=snd.samplerate)

cpdef SoundBuffer ms_decode(SoundBuffer snd):
    snd = snd.remix(2)
    cdef int length = len(snd)
    cdef double[:,:] out = np.zeros((length, 2), dtype='d')
    cdef double[:,:] frames = snd.frames
    for i in range(length):
        out[i, 0] = _l_decode(snd.frames[i, 0], snd.frames[i, 1])
        out[i, 1] = _r_decode(snd.frames[i, 0], snd.frames[i, 1])
    return SoundBuffer(out, channels=2, samplerate=snd.samplerate)

# Efficient power of two up/downsamplers
# From Fredrick Harris Multirate Signal Processing for Communication Systems
# Original paper with AG Constantinides
# https://www.researchgate.net/publication/259753999_Digital_Signal_Processing_with_Efficient_Polyphase_Recursive_All-pass_Filters
# Think homespun and less optimized version of Laurent De Soras HIIR
# Nothing fancy w/r/t group delay compensation, maybe someday

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef double _processHBAP1(HBAP* state, double sample):
    cdef double out = (sample - state.d2) * state.a0 + state.d1
    state.d1 = sample
    state.d2 = out
    return out

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef double _processHBAP2(HBAP* state, double sample):
    cdef double out1 = (sample - state.d2) * state.a0 + state.d1
    cdef double out2 = (out1 - state.d3) * state.a1 + state.d2
    state.d1 = sample
    state.d2 = out1
    state.d3 = out2
    return out2

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef void _initHBAP(HBAP* state):
    state.d1 = 0
    state.d2 = 0
    state.d3 = 0

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef SoundBuffer _decimate(SoundBuffer snd, int factor):

    # limit to defined range 1-5
    if (factor <= 0):
        return snd

    # create intermediary buffers for successive stages
    cdef double** stages = <double**>malloc(sizeof(double*) * factor)
    cdef int array_size = 2

    # create a buffer of allpass paths, 2 per stage
    cdef HBAP** filters = <HBAP**>malloc(sizeof(HBAP*) * factor * 2)

    cdef int i, j

    for i in range(factor):
        stages[i] = <double*>malloc(sizeof(double) * array_size)
        array_size *= 2
        if i < 2:
            filters[i * 2] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2].a0 = 0.0798664262025582
            filters[i * 2].a1 = 0.5453236511825826
            filters[i * 2].process = _processHBAP2

            filters[i * 2 + 1] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2 + 1].a0 = 0.283829344898100
            filters[i * 2 + 1].a1 = 0.834411891201724
            filters[i * 2 + 1].process = _processHBAP2
        else:
            filters[i * 2] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2].a0 = 0.11192
            filters[i * 2].process = _processHBAP1

            filters[i * 2 + 1] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2 + 1].a0 = 0.53976
            filters[i * 2 + 1].process = _processHBAP1

        _initHBAP(filters[i * 2])
        _initHBAP(filters[i * 2 + 1])


    cdef int oversample = <int>(2**factor)

    cdef int length_error = int(len(snd)) % oversample
    cdef int pad_size = (oversample-length_error)

    cdef int new_length = len(snd)//oversample
    snd = snd.pad(after=(pad_size + 1), samples=True)

    cdef int channels = snd.channels

    cdef double[:,:] out = np.zeros((new_length, channels), dtype='d')
    cdef double[:,:] frames = memoryview(snd)

    cdef int c, m, n, stage
    cdef int buflength = oversample//2

    # for each channel
    for c in range(channels):
        # for each sample in the smaller decimated buffer
        for i in range(new_length):
            buflength = oversample//2
            # grab the samples to decimate (wish this could be wrapped into the first decimation stage better)
            for j in range(oversample):
                stages[factor - 1][j] = frames[i * oversample + j][c]
            # perform successive decimation by 2 stages
            stage = factor - 1
            while stage > 0:
                for n in range(buflength):
                    stages[stage - 1][n] = (filters[stage * 2].process(filters[stage * 2], stages[stage][n * 2 + 1]) + \
                        filters[stage * 2 + 1].process(filters[stage * 2 + 1], stages[stage][n * 2])) * .5 
                buflength //= 2
                stage -= 1

            out[i][c] = (filters[0].process(filters[0], stages[0][1]) + filters[1].process(filters[1], stages[0][0])) * .5 

    for i in range(factor):
        free(stages[i])
        free(filters[i*2])
        free(filters[i*2 + 1])
    free(filters)
    free(stages)

    return SoundBuffer(out, channels=snd.channels, samplerate=(snd.samplerate / oversample))

cpdef SoundBuffer decimate(SoundBuffer snd, int factor):
    return _decimate(snd, factor)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef SoundBuffer _upsample(SoundBuffer snd, int factor):

    # same setup as decimator
    if (factor <= 0):
        return snd
    cdef double** stages = <double**>malloc(sizeof(double*) * factor)
    cdef int array_size = 2
    cdef HBAP** filters = <HBAP**>malloc(sizeof(HBAP*) * factor * 2)
    cdef int i, j
    for i in range(factor):
        stages[i] = <double*>malloc(sizeof(double) * array_size)
        array_size *= 2
        if i < 2:
            filters[i * 2] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2].a0 = 0.0798664262025582
            filters[i * 2].a1 = 0.5453236511825826
            filters[i * 2].process = _processHBAP2

            filters[i * 2 + 1] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2 + 1].a0 = 0.283829344898100
            filters[i * 2 + 1].a1 = 0.834411891201724
            filters[i * 2 + 1].process = _processHBAP2
        else:
            filters[i * 2] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2].a0 = 0.11192
            filters[i * 2].process = _processHBAP1

            filters[i * 2 + 1] = <HBAP*>malloc(sizeof(HBAP))
            filters[i * 2 + 1].a0 = 0.53976
            filters[i * 2 + 1].process = _processHBAP1
        _initHBAP(filters[i * 2])
        _initHBAP(filters[i * 2 + 1])
    
    cdef int oversample = <int>(2**factor)
    # no need to pad
    cdef int old_length = len(snd)
    cdef int new_length = old_length * oversample
    cdef int channels = snd.channels
    cdef double[:,:] out = np.zeros((new_length, channels), dtype='d')
    cdef double[:,:] frames = snd.frames
    cdef int c, m, n, stage, buflength

    # transpose of the decimator
    for c in range(channels):
        # for each sample in the smaller source buffer
        for i in range(old_length):
            # do the first stage of upsampling
            stages[0][0] = filters[0].process(filters[0], frames[i][c])
            stages[0][1] = filters[1].process(filters[1], frames[i][c])
            # perform successive upsampling by 2 stages
            stage = 1
            buflength = 2
            while stage < factor:
                for n in range(buflength):
                    stages[stage][2 * n] = filters[stage * 2].process(filters[stage * 2], stages[stage - 1][n])
                    stages[stage][2 * n + 1] = filters[stage * 2 + 1].process(filters[stage * 2 + 1], stages[stage - 1][n])
                buflength *= 2
                stage += 1
            # copy upsampled buffer
            for j in range(oversample):
                out[i * oversample + j][c] = stages[factor - 1][j]

    for i in range(factor):
        free(stages[i])
        free(filters[i*2])
        free(filters[i*2 + 1])
    free(filters)
    free(stages)

    return SoundBuffer(out, channels=snd.channels, samplerate=(snd.samplerate * oversample))

cpdef SoundBuffer upsample(SoundBuffer snd, int factor):
    return _upsample(snd, factor)

# arbitrary resampler
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.initializedcheck(False)
cdef SoundBuffer _resample(SoundBuffer snd, double ratio, int quality, bint resample):
    if (ratio == 0) or (ratio is None) or (snd is None): return snd

    cdef double factor = 1.0/ratio
    cdef int new_length = <int>(factor * len(snd))

    cdef double changesr = 1.0
    if resample: changesr = factor

    if quality < 0: quality = 0
    cdef lpbli_t * bli = LPInterpolation.bli_create(quality, 0)
    bli.table_length = len(snd)
    bli.resampling_factor=factor

    cdef lpbuffer_t * out = LPBuffer.create(new_length, snd.channels, snd.samplerate)
    cdef double[:,:] sndview = memoryview(snd)
    cdef lpbuffer_t * chan

    cdef int c, i
    cdef double position
    for c in range(snd.channels):
        chan = to_window(sndview[c,:])
        position = 0
        for i in range(new_length):
            out.data[i * snd.channels + c] = LPInterpolation.bli(bli, chan, position)
            position += ratio
        LPBuffer.destroy(chan)

    LPInterpolation.bli_destroy(bli)

    snd.samplerate *= changesr

    return snd.fromlpbuffer(out)

cpdef SoundBuffer resample(SoundBuffer snd, double ratio, int quality=5):
    return _resample(snd, ratio, quality, True)

cpdef SoundBuffer repitch(SoundBuffer snd, double ratio, int quality=5):
    return _resample(snd, ratio, quality, False)

cdef SoundBuffer _vspeed2(SoundBuffer snd, object speed, int quality, bint normalize):
    if (speed == 0) or (speed is None) or (snd is None): return snd

    cdef int channels = snd.channels
    cdef int length = len(snd)
    cdef int samplerate = snd.samplerate

    cdef lpbuffer_t * _speed = to_window(speed)
    cdef double speed_average = 0
    cdef size_t i
    if _speed.length > 1:
        for i in range(1, _speed.length):
            speed_average += (_speed.data[i] + _speed.data[i - 1]) * .5
        speed_average /= (_speed.length - 1)
        if speed_average == 0: speed_average = .5

    else:
        speed_average = abs(_speed.data[0])
    
    cdef double factor = 1.0/abs(speed_average)
    cdef double normalizer
    if normalize: normalizer = abs(speed_average)
    else: normalizer = 1
    cdef size_t new_length = <size_t>(factor * length * normalizer)

    cdef double speed_inc = (_speed.length - 1) / new_length

    if quality < 0: quality = 0
    cdef lpbli_t * bl_data = LPInterpolation.bli_create(quality, 0)
    bl_data.table_length = length
    bl_data.resampling_factor = 1

    cdef lpbuffer_t * out = LPBuffer.create(new_length, snd.channels, snd.samplerate)
    cdef double[:,:] frames = np.asarray(snd.frames).T

    cdef int c
    cdef double position, speed_pos, inc
    cdef lpbuffer_t * chan
    for c in range(snd.channels):
        chan = to_window(frames[c])
        position = 0
        speed_pos = 0
        for i in range(new_length):
            out.data[i * snd.channels + c] = LPInterpolation.bli(bl_data, chan, position)
            speed_pos += speed_inc
            inc = LPInterpolation.linear(_speed, speed_pos)
            position += inc / normalizer
            while position < 0:
                position += length
            while position >= length:
                position -= length
            if abs(inc) < 1:
                bl_data.resampling_factor = 1
            else:
                bl_data.resampling_factor = abs(1/inc)
        LPBuffer.destroy(chan)

    LPInterpolation.bli_destroy(bl_data)
    LPBuffer.destroy(_speed)
    return snd.fromlpbuffer(out)

cpdef SoundBuffer vspeed2(SoundBuffer snd, object speed, int quality=5, bint normalize=False):
    return _vspeed2(snd, speed, quality, normalize)


cpdef SoundBuffer weave(SoundBuffer snd, double threshold=0.1, bint above=True):
    # Only output samples above or below the threshold
    # Inspired by the Wovenland 2 recordings by Toshiya Tsunoda & Taku Unami

    cdef long length = len(snd)
    cdef int channels = snd.channels
    cdef int samplerate = snd.samplerate

    cdef double[:,:] out = np.zeros((length, channels), dtype='d')

    cdef long i = 0
    cdef long c = 0

    if above:
        for c in range(channels):
            for i in range(length):
                if abs(snd.frames[i,c]) >= threshold:
                    out[i,c] = snd.frames[i,c]

    else:
        for c in range(channels):
            for i in range(length):
                if abs(snd.frames[i,c]) <= threshold:
                    out[i,c] = snd.frames[i,c]

    return SoundBuffer(out, channels=channels, samplerate=samplerate)

