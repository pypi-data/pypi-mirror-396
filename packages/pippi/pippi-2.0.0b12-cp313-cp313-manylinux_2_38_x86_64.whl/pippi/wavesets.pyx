# cython: language_level=3, cdivision=True, wraparound=False, boundscheck=False, initializedcheck=False

from pippi.soundbuffer cimport SoundBuffer, to_wavetable, to_window
from pippi.rand cimport rand
from pippi.defaults cimport DEFAULT_CHANNELS, DEFAULT_SAMPLERATE

from libc.math cimport signbit
from libc.stdlib cimport malloc, free
from libc.string cimport memset
import numpy as np
cimport numpy as np

np.import_array()

"""
cdef class Waveset:
    def __cinit__(
            Waveset self, 
            object values=None, 
            object crossings=3, 
            int offset=-1,
            int limit=-1, 
            int modulo=1, 
            int samplerate=-1,
            list wavesets=None,
        ):

        self.samplerate = samplerate
        self.crossings = to_window(crossings)
        self.offset = offset
        self.limit = limit
        self.modulo = modulo
        self.waveset_count = 0

        memset(self.wavesets, 0, sizeof(self.wavesets))

        if values is not None:
            self._load(values)
        #elif wavesets is not None:
        #    self._import(wavesets)

    def __getitem__(self, position):
        return self.wavesets[position]

    def __iter__(self):
        return iter(self.wavesets)

    def __len__(self):
        return len(self.wavesets)

    cpdef Waveset copy(Waveset self):
        cdef Waveset copy = Waveset(samplerate=self.samplerate, wavesets=self.wavesets)
        copy.max_length = self.max_length
        copy.min_length = self.min_length
        return copy

"""

cpdef list to_wavesets(object values, object crossings=3, int offset=-1, int limit=-1, int modulo=1):
    cdef double original_mag = 0
    cdef double val, last
    cdef int crossing_count=0, waveset_count=0, mod_count=0, waveset_output_count=0, offset_count=0
    cdef int i=1, start=0, end=0

    cdef lpbuffer_t * crossingsbuf = to_window(crossings)

    cdef list wavesets = []

    cdef SoundBuffer src = SoundBuffer(values)
    src = src.remix(1)

    cdef double pos = 0
    cdef int _crossings = <int>crossingsbuf.data[0]
    cdef int length = len(src)
    last = src.buffer.data[0]

    while i < length:
        if (signbit(last) and not signbit(src.buffer.data[i])) or (not signbit(last) and signbit(src.buffer.data[i])):
            crossing_count += 1

            pos = <double>start / length
            _crossings = <int>LPInterpolation.trunc_pos(crossingsbuf, pos)
            if crossing_count >= _crossings:
                waveset_count += 1
                mod_count += 1
                crossing_count = 0

                if mod_count == modulo:
                    mod_count = 0
                    end = i

                    if offset_count <= offset:
                        offset_count += 1
                        continue

                    wavesets += [ src[start:end] ]
                    waveset_output_count += 1

                    if limit == waveset_output_count:
                        break

                start = i

        last = src.buffer.data[i]
        i += 1

    if end < length and limit < waveset_output_count:
        wavesets += [ src[end:length] ]

    LPBuffer.destroy(crossingsbuf)
    return wavesets


cpdef list interleave(list a, list b):
    cdef int i = 0
    cdef list interleaved = []
    cdef int shortest = min(len(a), len(b))
    for i in range(shortest):
        interleaved += [ a[i], b[i] ]
    return interleaved

cpdef list stretch(list wavesets, object factor=2.0):
    cdef int i, repeat
    cdef double pos = 0
    cdef list out = []
    cdef lpbuffer_t * curve = to_window(factor)

    cdef int num_wavesets = len(wavesets)
    for i in range(num_wavesets):
        pos = <double>i / num_wavesets
        repeat = <int>LPInterpolation.linear_pos(curve, pos)
        if repeat == 1:
            out += [ wavesets[i] ]
        elif repeat < 1:
            continue
        else:
            out += [ wavesets[i] ] * repeat

    LPBuffer.destroy(curve)
    return out

cpdef list retrograde(list wavesets):
    cdef list out = []
    for w in wavesets:
        out += [ w.reverse() ]
    return out

#cpdef void invert(Waveset self):
#    pass

"""
    cpdef SoundBuffer harmonic(Waveset self, list harmonics=None, list weights=None):
        if harmonics is None:
            harmonics = [1,2,3]

        if weights is None:
            weights = [1,0.5,0.25]

        cdef list out = []
        cdef int i, length, j, k, h, plength
        cdef double maxval
        cdef double[:] partial
        cdef double[:] cluster

        for i in range(len(self.wavesets)):
            length = len(self.wavesets[i])
            maxval = max(np.abs(self.wavesets[i])) 
            cluster = np.zeros(length, dtype='d')
            for h in harmonics:
                plength = length * h
                partial = np.zeros(plength, dtype='d')
                for j in range(h):
                    for k in range(length):
                        partial[k*j] = self.wavesets[i][k] * maxval

                partial = interpolation._linear(partial, length)

                for j in range(length):
                    cluster[j] += partial[j]

            for j in range(length):
                cluster[j] *= maxval

            out += [ cluster ]

        return self.render(out)
"""

"""
cpdef list replace(list wavesets, object waveforms):
    cdef double[:] wt
    cdef list out = []
    cdef int i, wi, length
    cdef int numwavesets = len(wavesets)
    cdef int numwaveforms = len(waveforms)
    cdef double maxval, wmaxval, pos
    cdef double[:] replacement

    for i in range(numwavesets):
        pos = <double>i / numwavesets
        wi = <int>(pos * numwaveforms)
        length = len(self.wavesets[i])
        maxval = max(np.abs(self.wavesets[i])) 
        wt = to_wavetable(waveforms[wi])
        wmaxval = max(np.abs(wt)) 
        replacement = interpolation._linear(wt, length)

        for j in range(length):
            replacement[j] *= (maxval / wmaxval)

        out += [ replacement ]

    return self.render(out)

    cpdef SoundBuffer substitute(Waveset self, object waveform):
        cdef double[:] wt = to_wavetable(waveform)
        cdef list out = []
        cdef int i, length
        cdef double maxval
        cdef double[:] replacement

        for i in range(len(self.wavesets)):
            length = len(self.wavesets[i])
            maxval = max(np.abs(self.wavesets[i])) 
            replacement = interpolation._linear(wt, length)

            for j in range(length):
                replacement[j] *= maxval

            out += [ replacement ]

        return self.render(out)

    cpdef SoundBuffer morph(Waveset self, Waveset target, object curve=None):
        if curve is None:
            curve = SINE

        cdef double[:] wt = to_window(curve)
        cdef int slength = len(self)
        cdef int tlength = len(target)
        cdef int maxlength = max(slength, tlength)
        cdef int i=0, si=0, ti=0
        cdef double prob=0, pos=0
        cdef list out = []

        while i < maxlength:
            pos = <double>i / maxlength
            prob = interpolation._linear_pos(wt, pos)
            if rand(0,1) > prob:
                si = <int>(pos * slength)
                out += [ self[si] ]
            else:
                ti = <int>(pos * tlength)
                out += [ target[ti] ]

            i += 1

        return self.render(out)
"""

