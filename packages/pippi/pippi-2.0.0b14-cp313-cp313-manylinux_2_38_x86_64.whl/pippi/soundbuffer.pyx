#cython: language_level=3

from cpython cimport Py_buffer
from libc.stdint cimport uintptr_t
import numbers
import warnings

cimport cython
from cpython.array cimport array, clone
cimport numpy as np
import numpy as np
import soundfile as sf

from pippi.defaults cimport DEFAULT_WTSIZE, DEFAULT_CHANNELS, DEFAULT_SAMPLERATE
from pippi.fx cimport softclip2
from pippi import graph, rand
from pippi cimport microsound


cdef dict WT_FLAGS = {
    'sine': WT_SINE,
    'cos': WT_COS,
    'square': WT_SQUARE,
    'tri': WT_TRI,
    'tri2': WT_TRI2,
    'saw': WT_RSAW,
    'rsaw': WT_RSAW,
    'rnd': WT_RND,
}

cdef dict WIN_FLAGS = {
    'sine': WIN_SINE,
    'sineine': WIN_SINEIN,
    'sineout': WIN_SINEOUT,
    'cos': WIN_COS,
    'tri': WIN_TRI, 
    'phasor': WIN_PHASOR, 
    'pluckin': WIN_PLUCKIN, 
    'pluckout': WIN_PLUCKOUT, 
    'hann': WIN_HANN, 
    'hannin': WIN_HANNIN, 
    'hannout': WIN_HANNOUT, 
    'hamm': WIN_HAMM,
    'bart': WIN_BART,
    'black': WIN_BLACK,
    'sinc': WIN_SINC,
    'gauss': WIN_GAUSS,
    'gaussin': WIN_GAUSSIN,
    'gaussout': WIN_GAUSSOUT,
    'rnd': WIN_RND,
    'saw': WIN_SAW,
    'rsaw': WIN_RSAW,
}

cdef dict PAN_METHODS = {
    'constant': PANMETHOD_CONSTANT,
    'linear': PANMETHOD_LINEAR,
    'sine': PANMETHOD_SINE,
    'gogins': PANMETHOD_GOGINS
}

cdef int to_pan_method(str name):
    try:
        return PAN_METHODS[name]
    except KeyError:
        return PANMETHOD_CONSTANT

cdef int to_win_flag(str name):
    try:
        return WIN_FLAGS[name]
    except KeyError:
        return WIN_SINE

cdef int to_wt_flag(str name):
    try:
        return WT_FLAGS[name]
    except KeyError:
        return WT_SINE

cdef lpbuffer_t * to_window(object o, size_t length=0):
    cdef lpbuffer_t * out
    if length <= 0:
        length = DEFAULT_WTSIZE

    if isinstance(o, str):
        out = LPWindow.create(to_win_flag(o), length)
    else:
        out = to_lpbuffer(o, length, 1)

    return out

cdef lpbuffer_t * to_wavetable(object o, size_t length=0):
    cdef lpbuffer_t * out
    if length <= 0:
        length = DEFAULT_WTSIZE

    if isinstance(o, str):
        out = LPWavetable.create(to_wt_flag(o), length)
    else:
        out = to_lpbuffer(o, length, 1)

    return out

cdef lpbuffer_t * to_lpbuffer(object o, size_t length, int channels=DEFAULT_CHANNELS, int samplerate=DEFAULT_SAMPLERATE):
    cdef lpbuffer_t * out
    cdef lpbuffer_t * bit
    cdef size_t i, olen
    cdef size_t wt_length
    cdef double phase, frac
    cdef size_t idx

    if o is None:
        return NULL

    if isinstance(o, numbers.Real):
        out = LPBuffer.create_from_float(<lpfloat_t>o, length, channels, samplerate)

    elif isinstance(o, SoundBuffer):
        #(<SoundBuffer>o).moved = True
        #return (<SoundBuffer>o).buffer
        return LPBuffer.clone((<SoundBuffer>o).buffer)

    elif isinstance(o, list):
        length = len(o)
        if isinstance(o[0], list) or isinstance(o[0], tuple):
            out = LPBuffer.create(length, channels, samplerate)
            channels = len(o[0])
            for i in range(length):
                for c in range(channels):
                    out.data[i * channels + c] = o[i][c]
        elif isinstance(o[0], str):
            channels = len(o)
            out = LPBuffer.create(DEFAULT_WTSIZE, channels, samplerate)
            for c, s in enumerate(o):
                bit = to_window(s, DEFAULT_WTSIZE)
                for i in range(<size_t>DEFAULT_WTSIZE):
                    out.data[i * channels + c] = bit.data[i]
                LPBuffer.destroy(bit)
        else:
            out = LPBuffer.create(length, channels, samplerate)
            for i in range(length):
                out.data[i] = <lpfloat_t>o[i]

    elif isinstance(o, np.ndarray):
        if len(o.shape) == 1:
            channels = 1
        else:
            channels = o.shape[1]
        out = LPBuffer.create(length, channels, samplerate)
        olen = len(o)
        for i in range(length):
            if length >= olen:
                break
            for c in range(channels):
                out.data[i * channels + c] = o[i * channels + c]

    elif hasattr(o, '__len__') and hasattr(o, 'shape'):
        # Handle memoryview slices and other array-like objects
        if len(o.shape) == 1:
            # 1D memoryview
            channels = 1
            length = min(length, <size_t>len(o))
            out = LPBuffer.create(length, channels, samplerate)
            for i in range(length):
                out.data[i] = <lpfloat_t>o[i]
        else:
            # 2D memoryview
            channels = o.shape[1]
            length = min(length, <size_t>o.shape[0])
            out = LPBuffer.create(length, channels, samplerate)
            for i in range(length):
                for c in range(channels):
                    out.data[i * channels + c] = <lpfloat_t>o[i, c]

    else:
        raise NotImplementedError(f'Invalid type {type(o)}')

    return out


class SoundBufferError(Exception):
    pass

# TODO restore these from old Wavetable class
#   - scale(fromlow, fromhigh, tolow, tohigh, log)
#   - snap(mult, pattern)
#   - interp(pos, method)
#   - harmonics(harmonics, weights)
#   - drink(width, minval, maxval)

#@cython.freelist(32)
@cython.final
cdef class SoundBuffer:
    def __cinit__(SoundBuffer self, 
            object frames=None, 
            double length=-1, 
            int channels=DEFAULT_CHANNELS, 
            int samplerate=DEFAULT_SAMPLERATE, 
            str filename=None, 
            double start=0, 
            double[:,:] buf=None
        ):

        cdef size_t framelength
        cdef size_t offset
        cdef double[:] src_view_1d
        cdef double[:,:] src_view_2d
        cdef size_t i, c

        self.moved = False

        if filename is not None:
            self._filename = filename
            # Filename will always override frames input
            if length > 0 and start > 0:
                info = sf.info(filename)
                samplerate = info.samplerate
                framelength = <size_t>(length * samplerate)
                offset = <size_t>(start * samplerate)
                frames, _ = sf.read(filename, frames=int(framelength), start=int(offset), dtype='float64', fill_value=0, always_2d=True)
            elif length > 0 and start == 0:
                info = sf.info(filename)
                samplerate = info.samplerate
                framelength = <size_t>(length * samplerate)
                frames, _ = sf.read(filename, frames=int(framelength), dtype='float64', fill_value=0, always_2d=True)
            else:
                frames, samplerate = sf.read(filename, dtype='float64', fill_value=0, always_2d=True)
                framelength = len(frames)

            channels = frames.shape[1]

        if frames is None and length > 0:
            # Create a silent buffer of the given length
            framelength = <size_t>(length * samplerate)
            self.buffer = LPBuffer.create(framelength, channels, samplerate)

        elif frames is not None:
            # Try to fill the buffer from the given frames object
            try:
                frames = np.asarray(frames, dtype='d') # FIXME there's probably a more direct way to do this?
                framelength = len(frames)
                channels = 1
                if len(frames.shape) > 1: 
                    channels = frames.shape[1] 

                self.buffer = LPBuffer.create(framelength, channels, samplerate)
                
                if channels == 1 and len(frames.shape) == 1:
                    src_view_1d = frames
                    for i in range(framelength):
                        self.buffer.data[i] = src_view_1d[i]
                else:
                    src_view_2d = frames
                    for i in range(framelength):
                        for c in range(<size_t>channels):
                            self.buffer.data[i * channels + c] = src_view_2d[i, c]

            except Exception as e:
                raise SoundBufferError('Invalid source for SoundBuffer. Got frames of type %s' % type(frames)) from e

        else:
            # A null buffer has 0 frames and is falsey
            self.buffer = NULL

    property channels:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return self.buffer.channels
            return 0

    property samplerate:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return self.buffer.samplerate
            return 0
        def __set__(SoundBuffer self, value):
            if self.buffer != NULL:
                self.buffer.samplerate = value

    property length:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return self.buffer.length
            return 0

    property dur:
        def __get__(SoundBuffer self):
            if self.buffer != NULL and self.samplerate > 0:
                return <double>self.buffer.length / <double>self.samplerate
            return 0

    property frames:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return memoryview(self)
            return None

    property min:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return <double>LPBuffer.min(self.buffer)
            return 0

    property max:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return <double>LPBuffer.max(self.buffer)
            return 0

    property mag:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return <double>LPBuffer.mag(self.buffer)
            return 0

    property avg:
        def __get__(SoundBuffer self):
            if self.buffer != NULL:
                return <double>LPBuffer.avg(self.buffer)
            return 0

    property filename:
        def __get__(SoundBuffer self):
            return self._filename

    @staticmethod
    cdef SoundBuffer _fromlpbuffer(lpbuffer_t * buffer, SoundBuffer meta=None):
        cdef SoundBuffer out = SoundBuffer.__new__(SoundBuffer, channels=buffer.channels, samplerate=buffer.samplerate)
        out.buffer = buffer
        if meta is not None:
            out._filename = meta._filename
        return out

    cdef fromlpbuffer(SoundBuffer self, lpbuffer_t * buffer):
        cdef SoundBuffer out = SoundBuffer.__new__(SoundBuffer, channels=buffer.channels, samplerate=buffer.samplerate)
        out.buffer = buffer
        if self._filename is not None:
            out._filename = self.filename
        return out

    @staticmethod
    def win(object w, double minvalue=0, double maxvalue=1, double length=0, double samplerate=DEFAULT_SAMPLERATE):
        cdef lpbuffer_t * out
        if length > 0:
            length *= samplerate

        out = to_window(w, <size_t>int(length))

        if minvalue != 0 and maxvalue != 1:
            LPBuffer.scale(out, 0, 1, minvalue, maxvalue)

        return SoundBuffer._fromlpbuffer(out)

    @staticmethod
    def wt(object w, double minvalue=-1, double maxvalue=1, double length=0, double samplerate=DEFAULT_SAMPLERATE):
        cdef lpbuffer_t * out
        if length > 0:
            length *= samplerate

        out = to_wavetable(w, <size_t>int(length))

        if minvalue != -1 and maxvalue != 1:
            LPBuffer.scale(out, -1, 1, minvalue, maxvalue)

        return SoundBuffer._fromlpbuffer(out)

    def __bool__(self):
        return bool(len(self))

    def __dealloc__(SoundBuffer self):
        # FIXME we could add a shared flag which would *create* the buffer in 
        # in shared memory from the start to avoid all copies...
        if not self.moved: # allow something else (like astrid) to claim ownership of the memory
            LPBuffer.destroy(self.buffer)

    def __repr__(self):
        return 'SoundBuffer(samplerate=%s, channels=%s, length=%s, dur=%.2f, filename=%s)' % (self.samplerate, self.channels, self.length, self.dur, self.filename)
    
    def __lt__(self, other):
        if not isinstance(other, SoundBuffer):
            try:
                return self.min < min(other)
            except ValueError as e:
                return NotImplemented
        return self.min < (<SoundBuffer>other).min

    def __le__(self, other):
        if not isinstance(other, SoundBuffer):
            return NotImplemented
        return self.min <= (<SoundBuffer>other).min

    def __eq__(self, other):
        if isinstance(other, SoundBuffer):
            #return LPBuffer.buffers_are_close(self.buffer, (<SoundBuffer>other).buffer, 1000) > 0
            return self.length == (<SoundBuffer>other).length
        return self.avg == other
        
    def __ne__(self, other):
        if isinstance(other, SoundBuffer):
            #return LPBuffer.buffers_are_close(self.buffer, (<SoundBuffer>other).buffer, 1000) == 0
            return self.length != (<SoundBuffer>other).length
        return self.avg != other

    def __gt__(self, other):
        if not isinstance(other, SoundBuffer):
            return NotImplemented
        return self.max > (<SoundBuffer>other).max

    def __ge__(self, other):
        if not isinstance(other, SoundBuffer):
            return NotImplemented
        return self.max >= (<SoundBuffer>other).max

    def __getbuffer__(SoundBuffer self, Py_buffer * buffer, int flags):
        cdef Py_ssize_t itemsize = sizeof(self.buffer.data[0])
        self.shape[0] = <Py_ssize_t>self.buffer.length
        self.shape[1] = <Py_ssize_t>self.buffer.channels
        self.strides[1] = <Py_ssize_t>(<char *>&(self.buffer.data[1]) - <char *>&(self.buffer.data[0]))
        self.strides[0] = self.buffer.channels * self.strides[1]

        buffer.buf = <char *>&(self.buffer.data[0])
        buffer.format = 'd'
        buffer.internal = NULL
        buffer.itemsize = itemsize
        buffer.len = self.buffer.length * self.buffer.channels
        buffer.ndim = 2
        buffer.obj = self
        buffer.readonly = 0
        buffer.shape = self.shape
        buffer.strides = self.strides
        buffer.suboffsets = NULL

    def __releasebuffer__(SoundBuffer self, Py_buffer * buffer):
        pass

    def __getitem__(self, position):
        cdef double[:,:] mv = memoryview(self)
        if isinstance(position, slice):
            start = position.start if position.start is not None else 0
            stop = position.stop if position.stop is not None else len(self)
            return SoundBuffer(mv[start:stop], channels=self.channels, samplerate=self.samplerate)
        elif isinstance(position, tuple):
            if len(position) == 1:
                return (self.buffer.data[position[0] * self.channels], self.buffer.data[position[0] * self.channels + 1])
            return self.buffer.data[position[0] * self.channels + position[1]]
        else:
            if position >= self.buffer.length:
                raise IndexError('Requested frame at position %d is beyond the end of the %d frame buffer.' % (position, self.buffer.length))
            elif position < 0:
                position = len(self) + position
            if self.channels == 1:
                return mv[position][0]
            return tuple([ mv[position][v] for v in range(self.channels) ])

    def __len__(self):
        return 0 if self.buffer == NULL else <Py_ssize_t>self.buffer.length

    def __add__(SoundBuffer self, object value):
        cdef Py_ssize_t i, c
        cdef lpbuffer_t * data
        cdef SoundBuffer tmp

        if self.buffer == NULL:
            if isinstance(value, numbers.Real):
                return SoundBuffer(channels=self.channels, samplerate=self.samplerate)

            elif isinstance(value, SoundBuffer):
                return value.copy()

            else:
                return SoundBuffer(value, channels=self.channels, samplerate=self.samplerate)

        if isinstance(value, numbers.Real):
            data = LPBuffer.create(self.buffer.length, self.buffer.channels, self.buffer.samplerate)
            LPBuffer.copy(self.buffer, data)
            LPBuffer.add_scalar(data, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            data = LPBuffer.concat(self.buffer, (<SoundBuffer>value).buffer)

        else:
            try:
                tmp = SoundBuffer(value)
                data = LPBuffer.concat(self.buffer, tmp.buffer)
            except Exception as e:
                return NotImplemented

        return self.fromlpbuffer(data)

    def __iadd__(SoundBuffer self, object value):
        cdef Py_ssize_t i, c

        if self.buffer == NULL:
            if isinstance(value, numbers.Real):
                return self

            elif isinstance(value, SoundBuffer):
                return value.copy()

            else:
                return SoundBuffer(value, channels=self.channels, samplerate=self.samplerate)


        if isinstance(value, numbers.Real):
            LPBuffer.add_scalar(self.buffer, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            LPBuffer.add(self.buffer, (<SoundBuffer>value).buffer)

        else:
            try:
                tmp = SoundBuffer(value)
                LPBuffer.add(self.buffer, tmp.buffer)
            except Exception as e:
                return NotImplemented

        return self

    def __radd__(SoundBuffer self, object value):
        return self + value

    def __sub__(SoundBuffer self, object value):
        cdef Py_ssize_t i, c
        cdef lpbuffer_t * data
        cdef SoundBuffer tmp

        if self.buffer == NULL:
            if isinstance(value, numbers.Real):
                return SoundBuffer(channels=self.channels, samplerate=self.samplerate)

            elif isinstance(value, SoundBuffer):
                return value.copy()

            else:
                return SoundBuffer(value, channels=self.channels, samplerate=self.samplerate)

        data = LPBuffer.create(self.buffer.length, self.buffer.channels, self.buffer.samplerate)
        LPBuffer.copy(self.buffer, data)

        if isinstance(value, numbers.Real):
            LPBuffer.subtract_scalar(data, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            LPBuffer.subtract(data, (<SoundBuffer>value).buffer)

        else:
            try:
                tmp = SoundBuffer(value)
                LPBuffer.subtract(data, tmp.buffer)
            except Exception as e:
                return NotImplemented

        return self.fromlpbuffer(data)

    def __isub__(SoundBuffer self, object value):
        cdef Py_ssize_t i, c

        if self.buffer == NULL:
            if isinstance(value, numbers.Real):
                return self

            elif isinstance(value, SoundBuffer):
                return value.copy()

            else:
                return SoundBuffer(value, channels=self.channels, samplerate=self.samplerate)

        if isinstance(value, numbers.Real):
            LPBuffer.subtract_scalar(self.buffer, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            LPBuffer.subtract(self.buffer, (<SoundBuffer>value).buffer)

        else:
            try:
                tmp = SoundBuffer(value)
                LPBuffer.subtract(self.buffer, tmp.buffer)
            except Exception as e:
                return NotImplemented

        return self

    def __rsub__(SoundBuffer self, object value):
        return self - value 

    def __mul__(SoundBuffer self, object value):
        cdef size_t i
        cdef int c
        cdef lpbuffer_t * data = LPBuffer.create(self.buffer.length, self.buffer.channels, self.buffer.samplerate)
        LPBuffer.copy(self.buffer, data)

        if isinstance(value, numbers.Real):
            LPBuffer.multiply_scalar(data, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            LPBuffer.multiply(data, (<SoundBuffer>value).buffer)

        else:
            try:
                for i in range(self.buffer.length):
                    for c in range(self.buffer.channels):
                        data.data[i * self.buffer.channels + c] *= value[i * self.buffer.channels + c]

            except IndexError as e:
                pass

            except Exception as e:
                return NotImplemented

        return self.fromlpbuffer(data)

    def __imul__(SoundBuffer self, object value):
        cdef size_t i
        cdef int c

        if isinstance(value, numbers.Real):
            LPBuffer.multiply_scalar(self.buffer, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            LPBuffer.multiply(self.buffer, (<SoundBuffer>value).buffer)

        else:
            try:
                for i in range(self.buffer.length):
                    for c in range(self.buffer.channels):
                        self.buffer.data[i * self.buffer.channels + c] *= value[i * self.buffer.channels + c]

            except IndexError as e:
                pass

            except Exception as e:
                return NotImplemented

        return self

    def __rmul__(SoundBuffer self, object value):
        return self * value

    def __and__(SoundBuffer self, object value):
        if not isinstance(value, SoundBuffer):
            return NotImplemented

        cdef lpbuffer_t * out

        out = LPBuffer.mix(self.buffer, (<SoundBuffer>value).buffer)
        return self.fromlpbuffer(out)

    def __iand__(SoundBuffer self, object value):
        if not isinstance(value, SoundBuffer):
            return NotImplemented

        cdef lpbuffer_t * old_buffer = self.buffer
        self.buffer = LPBuffer.mix(self.buffer, (<SoundBuffer>value).buffer)
        LPBuffer.destroy(old_buffer)
        return self

    def __rand__(SoundBuffer self, object value):
        return self & value

    def __truediv__(SoundBuffer self, object value):
        cdef lpbuffer_t * data
        cdef SoundBuffer tmp

        if self.buffer == NULL:
            if isinstance(value, numbers.Real):
                return SoundBuffer(channels=self.channels, samplerate=self.samplerate)

            elif isinstance(value, SoundBuffer):
                return value.copy()

            else:
                return SoundBuffer(value, channels=self.channels, samplerate=self.samplerate)

        data = LPBuffer.create(self.buffer.length, self.buffer.channels, self.buffer.samplerate)
        LPBuffer.copy(self.buffer, data)

        if isinstance(value, numbers.Real):
            LPBuffer.divide_scalar(data, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            LPBuffer.divide(data, (<SoundBuffer>value).buffer)

        else:
            try:
                tmp = SoundBuffer(value)
                LPBuffer.divide(data, (<SoundBuffer>value).buffer)
            except Exception as e:
                return NotImplemented

        return self.fromlpbuffer(data)

    def __itruediv__(SoundBuffer self, object value):
        if self.buffer == NULL:
            if isinstance(value, numbers.Real):
                return self

            elif isinstance(value, SoundBuffer):
                return value.copy()

            else:
                return SoundBuffer(value, channels=self.channels, samplerate=self.samplerate)

        if isinstance(value, numbers.Real):
            LPBuffer.divide_scalar(self.buffer, <lpfloat_t>value)

        elif isinstance(value, SoundBuffer):
            LPBuffer.divide(self.buffer, (<SoundBuffer>value).buffer)

        else:
            try:
                tmp = SoundBuffer(value)
                LPBuffer.divide(self.buffer, tmp.buffer)
            except Exception as e:
                return NotImplemented

        return self

    def __rtruediv__(SoundBuffer self, object value):
        return self / value 

    def blocks(SoundBuffer self, size_t blocksize):
        if blocksize <= 1:
            blocksize = 1

        cdef size_t frames_read = 0
        while frames_read < <size_t>len(self):
            yield self[frames_read:frames_read+blocksize]
            frames_read += blocksize

    def clear(SoundBuffer self):
        LPBuffer.clear(self.buffer)
        return self

    def clip(SoundBuffer self, double minval=-1, double maxval=1):
        LPBuffer.clip(self.buffer, minval, maxval)
        return self

    cpdef SoundBuffer convolve(SoundBuffer self, SoundBuffer impulse, bint norm=True):
        cdef lpbuffer_t * out

        if not isinstance(impulse, SoundBuffer):
            raise TypeError('Could not convolve impulse of type %s' % type(impulse))

        if impulse.channels != self.channels:
            impulse = impulse.remix(self.channels)

        out = LPSpectral.convolve(self.buffer, impulse.buffer)

        return self.fromlpbuffer(out)

    cpdef SoundBuffer diff(SoundBuffer self, SoundBuffer other):
        """ Compute the difference between this buffer and another buffer 
            Returns self - other
        """
        cdef lpbuffer_t * out
        cdef size_t outlength = min(self.buffer.length, other.buffer.length)
        
        out = LPBuffer.create(outlength, self.buffer.channels, self.buffer.samplerate)
        LPBuffer.copy(self.buffer, out)
        LPBuffer.diff(out, other.buffer)
        
        return self.fromlpbuffer(out)

    cpdef SoundBuffer fadein(SoundBuffer self, double amount):
        """ Apply an exponential fadein to the buffer 
            amount: 0-1 where 0 is no fade and 1 is full fade
        """
        cdef lpbuffer_t * out = LPBuffer.fadein(self.buffer, <lpfloat_t>amount)
        return self.fromlpbuffer(out)

    cpdef SoundBuffer fadeout(SoundBuffer self, double amount):
        """ Apply an exponential fadeout to the buffer 
            amount: 0-1 where 0 is no fade and 1 is full fade
        """
        cdef lpbuffer_t * out = LPBuffer.fadeout(self.buffer, <lpfloat_t>amount)
        return self.fromlpbuffer(out)

    def copy(SoundBuffer self):
        cdef lpbuffer_t * out
        out = LPBuffer.create(self.buffer.length, self.buffer.channels, self.buffer.samplerate)
        LPBuffer.copy(self.buffer, out)
        return self.fromlpbuffer(out)

    def cut(SoundBuffer self, double start=0, double length=0, size_t framelength=0):
        """ Copy a portion of this soundbuffer, returning 
            a new soundbuffer with the selected slice.
           
            The `start` param is a position in seconds to begin 
            cutting, and the `length` param is the cut length in seconds.

            Overflowing values that exceed the boundries of the source SoundBuffer 
            will return a SoundBuffer padded with silence so that the `length` param 
            is always respected.
        """
        if length == 0 and framelength == 0:
            return SoundBuffer(length=0, channels=self.channels, samplerate=self.samplerate) 

        if length < 0 or framelength < 0:
            return SoundBuffer(length=0, channels=self.channels, samplerate=self.samplerate) 

        while start < 0:
            start += length

        cdef size_t readstart = <size_t>(start * self.samplerate)
        cdef size_t outlength
        cdef lpbuffer_t * out

        if length == 0 and framelength < 0:
            outlength = framelength
        else:
            outlength = <size_t>(length * self.samplerate)

        if outlength == 0:
            return SoundBuffer()

        out = LPBuffer.cut(self.buffer, readstart, outlength)
        return self.fromlpbuffer(out)

    def fcut(SoundBuffer self, int start=0, int length=1):
        """ Copy a portion of this soundbuffer, returning 
            a new soundbuffer with the selected slice.

            Identical to `cut` except `start` and `length` 
            should be given in frames instead of seconds.
        """
        cdef lpbuffer_t * out
        if length <= 0:
            return SoundBuffer()
        while start < 0:
            start += length
        out = LPBuffer.cut(self.buffer, start, length)
        return self.fromlpbuffer(out)

    def rcut(SoundBuffer self, double length=0, int framelength=0):
        """ Copy a portion of this SoundBuffer of the 
            given length in seconds starting from a random 
            position within it. 
            
            This will always return a complete SoundBuffer 
            without overflows or added silence, and the entire 
            sound will be returned without added silence if a length 
            that exceeds the length of the source SoundBuffer is given -- 
            unlike SoundBuffer.cut() which will pad results with silence 
            to preserve the length param if an invalid or overflowing offset 
            position is given.
        """
        cdef size_t cut_length, cut_start
        if length <= 0 and framelength <= 0:
            return SoundBuffer()

        if length <= 0 and framelength > 0:
            cut_length = framelength
        elif length > 0 and framelength <= 0:
            cut_length = <size_t>(length * self.samplerate)
        else:
            return SoundBuffer()

        if cut_length >= self.length:
            cut_length = self.length

        if cut_length == 0:
            return SoundBuffer()

        cut_start = rand.randint(0, self.length - cut_length)
        return self[cut_start:cut_start+cut_length]

    def dub(SoundBuffer self, object sounds, double pos=0, size_t framepos=0):
        """ Dub a sound or iterable of sounds into this soundbuffer
            starting at the given position in fractional seconds.

                >>> snd.dub(snd2, 3.2)

            To dub starting at a specific frame position use:

                >>> snd.dub(snd3, framepos=111)
        """
        cdef int numsounds, i
        cdef lpfloat_t samplerate = self.samplerate

        if samplerate <= 0:
            if isinstance(sounds, SoundBuffer):
                samplerate = sounds.samplerate
            elif isinstance(sounds, list):
                samplerate = sounds[0].samplerate
            else:
                raise NotImplementedError(f'Invalid type {type(sounds)=}')

        if pos > 0:
            framepos = <size_t>(pos * samplerate)

        return self.fdub(sounds, framepos)

    cpdef SoundBuffer diffuse_into(SoundBuffer self, SoundBuffer src, object pan=0.5, int channel=0, str method=None):
        """ Diffuse a channel from a source buffer into this multichannel buffer (in-place mix).

        This takes a source buffer, reads a single channel from it, and mixes it into this
        multichannel buffer, positioning it across channels based on the pan value which can
        modulate over time.

        Args:
            src: SoundBuffer to read from
            pan: pan position from 0 (first channel) to 1 (last channel)
                 Can be a float, list, or SoundBuffer for modulation over time
            channel: which channel to read from src (default: 0)
            method: 'constant' for constant power (default), 'linear' for linear

        Returns:
            self (for method chaining)

        Examples:
            >>> # Create multichannel buffer and diffuse mono sound into it
            >>> out = SoundBuffer(length=2.0, channels=3)
            >>> mono = SoundBuffer(filename='sound.wav')
            >>> out.diffuse_into(mono, pan=0.5)
            >>>
            >>> # Chain multiple diffusions with different pan positions
            >>> out.diffuse_into(sound1, pan=0.0).diffuse_into(sound2, pan=1.0)
            >>>
            >>> # Use channel 2 from a multichannel source
            >>> out.diffuse_into(multichannel_src, pan=0.5, channel=2)
            >>>
            >>> # With modulation
            >>> lfo = SoundBuffer.win('sine', length=mono.dur)
            >>> out.diffuse_into(mono, pan=lfo)
        """
        if method is None:
            method = 'constant'

        # Validate channel index
        if channel >= src.buffer.channels or channel < 0:
            raise ValueError(f"Channel index {channel} out of range for {src.buffer.channels}-channel source buffer")

        # Ensure source fits in output (resize output if needed)
        if src.buffer.length > self.buffer.length:
            self.buffer = LPBuffer.resize(self.buffer, src.buffer.length)

        cdef int _method = PANMETHOD_CONSTANT if method == 'constant' else PANMETHOD_LINEAR
        cdef lpbuffer_t * _pan = to_window(pan, len(src))
        cdef size_t i
        cdef lpfloat_t pos, pan_value, sample

        for i in range(src.buffer.length):
            pos = <lpfloat_t>i / src.buffer.length
            pan_value = LPInterpolation.linear_pos(_pan, pos)
            sample = src.buffer.data[i * src.buffer.channels + channel]
            LPFX.diffuse_into(self.buffer, i, sample, pan_value, _method)

        LPBuffer.destroy(_pan)
        return self

    cpdef SoundBuffer fdub(SoundBuffer self, object sounds, size_t framepos=0):
        cdef SoundBuffer source
        cdef size_t required_length
        
        if isinstance(sounds, SoundBuffer):
            source = <SoundBuffer>sounds
            required_length = framepos + source.buffer.length
            
            # Handle empty buffer case or resize 
            if not self or len(self) == 0 or self.buffer == NULL:
                self.buffer = LPBuffer.create(required_length, source.buffer.channels, source.buffer.samplerate)
            elif required_length > self.buffer.length:
                self.buffer = LPBuffer.resize(self.buffer, required_length)
                
            LPBuffer.dub(self.buffer, source.buffer, framepos)

        elif isinstance(sounds, numbers.Real):
            # For scalar dub, we only need one frame beyond framepos
            required_length = framepos + 1
            if not self or len(self) == 0 or self.buffer == NULL:
                self.buffer = LPBuffer.create(required_length, DEFAULT_CHANNELS, DEFAULT_SAMPLERATE)
            elif required_length > self.buffer.length:
                self.buffer = LPBuffer.resize(self.buffer, required_length)
                
            LPBuffer.dub_scalar(self.buffer, <lpfloat_t>sounds, framepos)

        else:
            numsounds = len(sounds)
            try:
                for i in range(numsounds):
                    source = <SoundBuffer>sounds[i]
                    required_length = framepos + source.buffer.length
                    
                    # Handle empty buffer case or resize for this sound
                    if self.buffer == NULL:
                        self.buffer = LPBuffer.create(required_length, source.buffer.channels, source.buffer.samplerate)
                    elif required_length > self.buffer.length:
                        self.buffer = LPBuffer.resize(self.buffer, required_length)
                        
                    LPBuffer.dub(self.buffer, source.buffer, framepos)

            except TypeError as e:
                raise TypeError('Please provide a SoundBuffer or list of SoundBuffers for dubbing') from e

        return self

    cpdef SoundBuffer remap(SoundBuffer self, tuple channels):
        """Remap channels from source buffer to create a new buffer.

        Args:
            channels: tuple of source channel indices for each output channel
                     e.g., (0, 0) creates stereo from mono channel 0
                          (1, 0) swaps left/right channels
                          (0, 1, 0) creates 3-channel from stereo, duplicating left

        Returns:
            A new SoundBuffer with remapped channels
        """
        cdef int channel_map[32]  # Support up to 32 channels
        cdef int num_channels = len(channels)
        cdef int i

        # Validate channel indices and populate map
        for i in range(num_channels):
            if channels[i] >= self.buffer.channels or channels[i] < 0:
                raise ValueError(f"Channel index {channels[i]} out of range for {self.buffer.channels}-channel buffer")
            channel_map[i] = channels[i]

        cdef lpbuffer_t * out = LPBuffer.create(self.buffer.length, num_channels, self.buffer.samplerate)
        LPBuffer.remap(out, self.buffer, num_channels, channel_map)
        return self.fromlpbuffer(out)

    cpdef tuple split(SoundBuffer self):
        """Split a multichannel buffer into individual mono buffers.

        Returns:
            A tuple of mono SoundBuffers, one for each channel

        Examples:
            >>> stereo = SoundBuffer(frames, channels=2)
            >>> left, right = stereo.split()
            >>>
            >>> multichannel = SoundBuffer(frames, channels=4)
            >>> ch0, ch1, ch2, ch3 = multichannel.split()
        """
        cdef int c
        cdef list mono_buffers = []
        cdef lpbuffer_t * mono
        cdef size_t i
        cdef int num_channels = self.buffer.channels

        if num_channels == 2:
            # Use optimized split2 for stereo
            return self.split2()

        # General case: extract each channel
        for c in range(num_channels):
            mono = LPBuffer.create(self.buffer.length, 1, self.buffer.samplerate)
            for i in range(self.buffer.length):
                mono.data[i] = self.buffer.data[i * num_channels + c]
            mono_buffers.append(self.fromlpbuffer(mono))

        return tuple(mono_buffers)

    cpdef tuple split2(SoundBuffer self):
        """Split a stereo buffer into two mono buffers using optimized C routine.

        Returns:
            A tuple of (left, right) mono SoundBuffers

        Raises:
            ValueError: If the buffer is not stereo (2 channels)

        Examples:
            >>> stereo = SoundBuffer(frames, channels=2)
            >>> left, right = stereo.split2()
        """
        if self.buffer.channels != 2:
            raise ValueError(f"split2() requires a stereo (2-channel) buffer, got {self.buffer.channels} channels")

        cdef lpbuffer_t * left = LPBuffer.create(self.buffer.length, 1, self.buffer.samplerate)
        cdef lpbuffer_t * right = LPBuffer.create(self.buffer.length, 1, self.buffer.samplerate)

        LPBuffer.split2(self.buffer, left, right)

        return (self.fromlpbuffer(left), self.fromlpbuffer(right))

    cpdef SoundBuffer remix(SoundBuffer self, int channels):
        channels = max(channels, 1)
        cdef lpbuffer_t * out = LPBuffer.remix(self.buffer, channels)
        return self.fromlpbuffer(out)

    cpdef SoundBuffer repeat(SoundBuffer self, size_t repeats):
        repeats = <size_t>max(repeats, <size_t>1)
        cdef lpbuffer_t * out = LPBuffer.repeat(self.buffer, repeats)
        return self.fromlpbuffer(out)

    cpdef SoundBuffer reverse(SoundBuffer self):
        return self.reversed()

    cpdef SoundBuffer reversed(SoundBuffer self):
        cdef lpbuffer_t * out = LPBuffer.reverse(self.buffer)
        return self.fromlpbuffer(out)

    cpdef SoundBuffer env(SoundBuffer self, object window=None):
        """ Apply an amplitude envelope
            to the sound of the given type.

            To modulate a sound with an arbitrary
            iterable, simply do:

                >>> snd * iterable

            Where iterable is a list, array, or SoundBuffer with
            the same # of channels and of any length
        """
        cdef lpbuffer_t * w
        cdef lpbuffer_t * out
        if window is None:
            window = 'sine'
        cdef int length = len(self)
        out = LPBuffer.create(length, self.channels, self.samplerate)
        LPBuffer.copy(self.buffer, out)
        w = to_window(window, length)
        LPBuffer.multiply(out, w)
        LPBuffer.destroy(w)
        return self.fromlpbuffer(out)

    cpdef SoundBuffer fill(SoundBuffer self, object src, int nperiods=1):
        cdef lpbuffer_t * _src = to_wavetable(src)
        LPBuffer.fill(self.buffer, _src, nperiods)
        LPBuffer.destroy(_src)
        return self

    cpdef SoundBuffer loop(SoundBuffer self, double length):
        cdef lpbuffer_t * out = LPBuffer.loop(self.buffer, <size_t>(length * self.samplerate))
        return self.fromlpbuffer(out)

    def grains(SoundBuffer self, double minlength, double maxlength=-1):
        """ Iterate over the buffer in fixed-size grains.
            If a second length is given, iterate in randomly-sized 
            grains, given the minimum and maximum sizes.
        """
        if minlength == maxlength or (minlength <= 0 and maxlength <= 0):
            return SoundBuffer([], channels=self.channels, samplerate=self.samplerate)

        if minlength > self.dur:
            minlength = self.dur

        if maxlength > 0 and maxlength > self.dur:
            maxlength = self.dur

        cdef size_t framesread = 0
        cdef size_t minframes = <size_t>(minlength * self.samplerate)
        cdef size_t grainlength = minframes
        cdef size_t maxframes

        if maxlength > 0:
            maxframes = <size_t>(maxlength * self.samplerate)
            while framesread < <size_t>len(self):
                grainlength = LPRand.randint(minframes, maxframes)
                yield self[framesread:framesread+grainlength]
                framesread += grainlength
        else:
            while framesread < <size_t>len(self):
                yield self[framesread:framesread+grainlength]
                framesread += grainlength

    def graph(SoundBuffer self, *args, **kwargs):
        return graph.write(self, *args, **kwargs)
    
    def mix(SoundBuffer self, object sounds):
        """ Mix this sound in place with an iterable of sounds
        """
        cdef SoundBuffer sound
        cdef int numsounds
        cdef int sound_index
        if isinstance(sounds, SoundBuffer):
            self &= sounds
        else:
            numsounds = len(sounds)
            try:
                for sound_index in range(numsounds):
                    self &= sounds[sound_index] 
            except TypeError as e:
                raise TypeError('Please provide a SoundBuffer or list of SoundBuffers for mixing') from e
        return self

    def pad(SoundBuffer self, double before=0, double after=0, bint samples=False):
        """ Pad this sound with silence at before or after
        """
        if before <= 0 and after <= 0: 
            return self

        cdef lpbuffer_t * out
        cdef size_t framebefore, frameafter

        if samples:
            framebefore = <size_t>before
            frameafter = <size_t>after
        else:
            framebefore = <size_t>(before * self.samplerate)
            frameafter = <size_t>(after * self.samplerate)

        out = LPBuffer.pad(self.buffer, framebefore, frameafter)
        return self.fromlpbuffer(out)

    def pan(SoundBuffer self, object pos=0.5, str method=None):
        """ Pan a stereo sound from `pos=0` (hard left) to `pos=1` (hard right)

            Different panning strategies can be chosen by passing a value to the `method` param.

            - `method='constant'` Constant (square) power panning. This is the default.
            - `method='linear'` Simple linear panning.
            - `method='sine'` Variation on constant power panning using sin() and cos() to shape the pan. _Taken from the floss manuals csound manual._
            - `method='gogins'` Michael Gogins' variation on the above which uses a different part of the sinewave. _Also taken from the floss csound manual!_
        """
        if method is None:
            method = 'constant'

        cdef int _method = to_pan_method(method)
        cdef lpbuffer_t * out
        cdef lpbuffer_t * _pos = to_window(pos)

        out = LPBuffer.create(len(self), self.channels, self.samplerate)
        LPBuffer.copy(self.buffer, out)
        LPBuffer.pan(out, _pos, _method)

        LPBuffer.destroy(_pos)
        return self.fromlpbuffer(out)

    def plot(SoundBuffer self):
        LPBuffer.plot(self.buffer)

    def skew(SoundBuffer self, double tip=0.5):
        cdef lpbuffer_t * out = LPBuffer.skew(self.buffer, tip)
        return self.fromlpbuffer(out)

    def softclip(SoundBuffer self):
        cdef lpfxsoftclip_t * sc = LPSoftClip.create()
        cdef size_t i
        cdef int c
        cdef lpfloat_t sample

        for i in range(self.buffer.length):
            for c in range(self.buffer.channels):
                sample = self.buffer.data[i * self.buffer.channels + c]
                sample = LPSoftClip.process(sc, sample)
                self.buffer.data[i * self.buffer.channels + c] = sample

        return self

    def softclip2(SoundBuffer self):
        return softclip2(self)

    def speed(SoundBuffer self, object speed, str interpolation=None):
        """ Change the speed of the sound
        """
        cdef lpbuffer_t * out
        #cdef int interpolation_scheme

        # TODO would be cool to be able to select the interpolator
        # like some pippi oscs allow.
        #if interpolation is None:
        #    interpolation = 'linear'
        #interpolation_scheme = to_interpolation_scheme(interpolation)

        cdef lpbuffer_t * _speed = to_window(speed)

        out = LPBuffer.varispeed(self.buffer, _speed)
        LPBuffer.destroy(_speed)
        return self.fromlpbuffer(out)

    def vspeed(SoundBuffer self, object speed, str interpolation=None):
        warnings.warn('SoundBuffer.vspeed() is deprecated. Please use SoundBuffer.speed()', DeprecationWarning)
        return self.speed(speed, interpolation)

    def resample(SoundBuffer self, size_t length):
        cdef lpbuffer_t * out = LPBuffer.resample(self.buffer, length)
        return self.fromlpbuffer(out)

    def taper(self, double start, double end=-1):
        cdef lpbuffer_t * out

        if start <= 0 and end <= 0:
            return self

        if end < 0:
            end = start

        out = LPBuffer.create(len(self), self.channels, self.samplerate)
        LPBuffer.copy(self.buffer, out)
        LPBuffer.taper(out, <size_t>(start * self.samplerate), <size_t>(end * self.samplerate))
        return self.fromlpbuffer(out)

    def toenv(SoundBuffer self, double window=0.01):
        cdef lpbuffer_t * out = LPBuffer.create(self.length, 1, self.samplerate)
        cdef lpenvelopefollower_t * env = LPEnvelopeFollower.create(window, self.samplerate)
        cdef int channels = self.channels
        cdef lpfloat_t sample = 0

        if channels == 1:
            for i in range(self.length):
                out.data[i] = LPEnvelopeFollower.process(env, self[i])
        else:
            for i in range(self.length):
                sample = 0
                for c in range(channels):
                    sample += self[i][c]
                sample /= channels
                out.data[i] = LPEnvelopeFollower.process(env, sample)

        LPEnvelopeFollower.destroy(env)

        return self.fromlpbuffer(out)

    def towavetable(SoundBuffer self, *args, **kwargs):
        warnings.warn('SoundBuffer.towavetable() is deprecated. Use SoundBuffers as wavetables directly. Please use SoundBuffer.remix(1) to mix down to a single channel.', DeprecationWarning)
        if self.channels == 1:
            return self
        cdef lpbuffer_t * out = LPBuffer.remix(self.buffer, 1)
        return self.fromlpbuffer(out)

    def trim(SoundBuffer self, bint start=False, bint end=True, double threshold=0, int window=4):
        """ Trim silence below a given threshold from the end (and/or start) of the buffer
        """
        cdef lpbuffer_t * out
        out = LPBuffer.trim(self.buffer, start, end, threshold, window);
        return self.fromlpbuffer(out)

    def cloud(SoundBuffer self, double length=-1, *args, **kwargs):
        """ Create a new Cloud from this SoundBuffer
        """
        return microsound.Formation(self, *args, **kwargs).play(length)

    def stretch(SoundBuffer self, double factor=1.0, *args, **kwargs):
        """ Time-stretch the buffer without changing pitch
        """
        new_length = self.dur * factor
        # Use cloud with speed=1/factor to stretch time
        kwargs['speed'] = 1.0 / factor
        return self.cloud(new_length, *args, **kwargs)

    def transpose(SoundBuffer self, double factor=1.0, *args, **kwargs):
        """ Pitch-shift the buffer without changing time
        """
        # Use cloud with speed=factor but keep original length
        kwargs['speed'] = factor
        return self.cloud(self.dur, *args, **kwargs)

    def write(self, unicode filename=None):
        """ Write the contents of this buffer to disk 
            in the given audio file format. (WAV, AIFF, AU)
        """
        sf.write(filename, np.asarray(self), self.samplerate)

