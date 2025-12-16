#cython: language_level=3

from libc.stdlib cimport malloc, free
from libc.string cimport memset
from libc cimport math

import numpy as np
cimport numpy as np

from pippi import dsp
from pippi cimport soundbuffer
from pippi.soundbuffer cimport SoundBuffer, to_window
from pippi.defaults cimport DEFAULT_SAMPLERATE

np.import_array()

cpdef SoundBuffer convolve(SoundBuffer snd, SoundBuffer impulse, bint norm=True):
    cdef lpbuffer_t * out

    if not isinstance(impulse, SoundBuffer):
        raise TypeError('Could not convolve impulse of type %s' % type(impulse))

    if impulse.channels != snd.channels:
        impulse = impulse.remix(snd.channels)

    out = LPSpectral.convolve(snd.buffer, impulse.buffer)

    return snd.fromlpbuffer(out)

cpdef tuple to_xy(SoundBuffer mag, SoundBuffer arg):
    cdef int channels = mag.channels
    cdef size_t length = len(mag)
    cdef double[:,:] _mag = mag.frames
    cdef double[:,:] _arg = arg.frames
    cdef double[:,:] real = np.zeros((length, channels), dtype='d')
    cdef double[:,:] imag = np.zeros((length, channels), dtype='d')

    cdef size_t i = 0
    cdef int c = 0

    for c in range(channels):
        for i in range(length):
            real[i,c] = _mag[i,c] * math.cos(_arg[i,c])
            imag[i,c] = _mag[i,c] * math.sin(_arg[i,c])

    return (
        SoundBuffer(real, channels=channels, samplerate=mag.samplerate), 
        SoundBuffer(imag, channels=channels, samplerate=mag.samplerate)
    )

cpdef tuple to_polar(SoundBuffer real, SoundBuffer imag):
    cdef int channels = real.channels
    cdef size_t length = len(real)
    cdef double[:,:] mag = np.zeros((length, real.channels), dtype='d')
    cdef double[:,:] arg = np.zeros((length, real.channels), dtype='d')
    cdef double[:,:] _real = real.frames
    cdef double[:,:] _imag = imag.frames

    cdef size_t i = 0
    cdef int c = 0

    for c in range(channels):
        for i in range(length):
            # Calculate the magnitude of the complex number
            mag[i,c] = math.sqrt((_real[i,c] * _real[i,c]) + (_imag[i,c] * _imag[i,c]))

            # Calculate the argument / angle of the complex vector
            if _real[i,c] == 0:
                arg[i,c] = 0
            else:
                arg[i,c] = math.atan(_imag[i,c] / _real[i,c])

    return (
        SoundBuffer(mag, channels=channels, samplerate=real.samplerate), 
        SoundBuffer(arg, channels=channels, samplerate=real.samplerate)
    )

cpdef SoundBuffer process(SoundBuffer snd, 
        double length=-1, 
        object callback=None, 
        object window=None, 
        int blocksize=4096
    ):
    if length < 0:
        length = snd.dur
    if window is None:
        window = 'hann'
    cdef lpbuffer_t * win = to_window(window)
    cdef lpbuffer_t * out = LPSpectral.process(snd.buffer, length, win, NULL, blocksize)
    LPBuffer.destroy(win)
    return snd.fromlpbuffer(out)

