#cython: language_level=3

#from pippi.bar import Bar
#from pippi.fm import FM
#from pippi.osc import Osc
#from pippi.osc2d import Osc2d
#from pippi.pulsar2d import Pulsar2d
#from pippi.pluck import Pluck
#from pippi.sineosc import SineOsc
#from pippi.tukey import Tukey

import numbers

#from pippi.soundpipe cimport _bar
from pippi.soundbuffer cimport * 
from pippi.rand cimport rand
#from pippi cimport interpolation


import numpy as np
cimport numpy as np
cimport cython
from cpython.array cimport array, clone
from libc cimport math

from pippi.defaults cimport (
    DEFAULT_SAMPLERATE, 
    DEFAULT_WTSIZE, 
    DEFAULT_CHANNELS, 
    MIN_PULSEWIDTH,
    PI
)

#cdef double _linear_point_osc(double[:] data, double phase, BLIData* bl_data) nogil:
#    return LPinterpolation.linear(data, phase)

cdef inline short DOUBLE_TO_SHORT(double x):
    return <int>(x*32768.0)

"""
cdef class Bar:
    def __cinit__(
            self, 
            object amp=1.0, 
            double stiffness=3.0,
            double decay=3.0,
            double leftclamp=1, 
            double rightclamp=1,
            double scan=0.25,
            double barpos=0.2,
            double velocity=500.0,
            double width=0.05,
            double loss=0.001,
            double phase=0,

            int wtsize=4096,
            int channels=DEFAULT_CHANNELS,
            int samplerate=DEFAULT_SAMPLERATE,
        ):

        self.wtsize = wtsize
        self.amp = to_window(amp, self.wtsize)

        self.stiffness = stiffness
        self.decay = decay
        self.leftclamp = leftclamp
        self.rightclamp = rightclamp
        self.scan = scan
        self.barpos = barpos
        self.velocity = velocity
        self.width = width
        self.loss = loss

        self.channels = channels
        self.samplerate = samplerate

    def play(self, length):
        framelength = <int>(length * self.samplerate)
        return self._play(framelength)

    cdef SoundBuffer _play(self, int length):
        cdef double[:,:] out = np.zeros((length, self.channels), dtype='d')
        return SoundBuffer(_bar(out, length, self.amp, self.stiffness, self.decay, self.leftclamp, self.rightclamp, self.scan, self.barpos, self.velocity, self.width, self.loss, self.channels), channels=self.channels, samplerate=self.samplerate)
"""

#@cython.freelist(32)
cdef class FM:
    """ Basic FM synth
    """
    def __cinit__(
            self, 
            object carrier=None, 
            object modulator=None, 
            object freq=440.0, 
            object ratio=1.0, 
            object index=None, 
            object amp=1.0, 
            double phase=0, 

            object freq_interpolator=None,

            int wtsize=4096,
            int channels=DEFAULT_CHANNELS,
            int samplerate=DEFAULT_SAMPLERATE,
        ):

        if carrier is None:
            carrier = 'sine'

        if modulator is None:
            modulator = 'sine'

        if index is None:
            index = 'hannout'

        self.freq = to_window(freq, self.wtsize)
        self.ratio = to_window(ratio, self.wtsize)
        self.index = to_window(index, self.wtsize)
        self.amp = to_window(amp, self.wtsize)

        # FIXME
        #if freq_interpolator is None:
        #    freq_interpolator = 'linear'
        #self.freq_interpolator = interpolation.get_point_interpolator(freq_interpolator)

        self.cwt_phase = phase
        self.mwt_phase = phase
        self.freq_phase = 0
        self.ratio_phase = 0
        self.index_phase = 0
        self.amp_phase = 0

        self.channels = channels
        self.samplerate = samplerate
        self.wtsize = wtsize

        self.carrier = to_wavetable(carrier, self.wtsize)
        self.modulator = to_wavetable(modulator, self.wtsize)

    def play(self, double length):
        cdef size_t framelength = <size_t>(length * self.samplerate)
        cdef size_t i = 0
        cdef double sample, freq, ratio, index, amp, mod, mfreq, cfreq
        cdef double ilength = 1.0 / framelength
        cdef double isamplerate = 1.0 / self.samplerate

        cdef size_t freq_boundry = <size_t>max(self.freq.length-1, <size_t>1)
        cdef size_t ratio_boundry = <size_t>max(self.ratio.length-1, <size_t>1)
        cdef size_t index_boundry = <size_t>max(self.index.length-1, <size_t>1)
        cdef size_t amp_boundry = <size_t>max(self.amp.length-1, <size_t>1)
        cdef size_t cwt_boundry = <size_t>max(self.carrier.length-1, <size_t>1)
        cdef size_t mwt_boundry = <size_t>max(self.modulator.length-1, <size_t>1)

        cdef double freq_phase_inc = ilength * freq_boundry
        cdef double ratio_phase_inc = ilength * ratio_boundry
        cdef double index_phase_inc = ilength * index_boundry
        cdef double amp_phase_inc = ilength * amp_boundry

        cdef double cwt_phase_inc = isamplerate * self.wtsize
        cdef double mwt_phase_inc = isamplerate * self.wtsize

        cdef lpbuffer_t * out = LPBuffer.create(framelength, self.channels, self.samplerate)

        for i in range(framelength):
            #freq = self.freq_interpolator(self.freq, self.freq_phase)
            freq = LPInterpolation.linear(self.freq, self.freq_phase)
            ratio = LPInterpolation.linear(self.ratio, self.ratio_phase)
            index = LPInterpolation.linear(self.index, self.index_phase)

            amp = LPInterpolation.linear(self.amp, self.amp_phase)
            mamp = freq * index * ratio

            mod = LPInterpolation.linear(self.modulator, self.mwt_phase) * mamp
            sample = LPInterpolation.linear(self.carrier, self.cwt_phase) * amp

            cfreq = freq + mod
            mfreq = freq * ratio

            self.freq_phase += freq_phase_inc
            self.ratio_phase += ratio_phase_inc
            self.index_phase += index_phase_inc
            self.amp_phase += amp_phase_inc

            self.cwt_phase += cfreq * cwt_phase_inc
            self.mwt_phase += mfreq * mwt_phase_inc

            if self.cwt_phase < 0:
                self.cwt_phase += cwt_boundry
            elif self.cwt_phase >= cwt_boundry:
                self.cwt_phase -= cwt_boundry

            while self.mwt_phase >= mwt_boundry:
                self.mwt_phase -= mwt_boundry

            while self.amp_phase >= amp_boundry:
                self.amp_phase -= amp_boundry

            while self.freq_phase >= freq_boundry:
                self.freq_phase -= freq_boundry

            while self.ratio_phase >= ratio_boundry:
                self.ratio_phase -= ratio_boundry

            while self.index_phase >= index_boundry:
                self.index_phase -= index_boundry

            for channel in range(self.channels):
                out.data[i * self.channels + channel] = sample

        return SoundBuffer._fromlpbuffer(out)

    def __dealloc__(self):
        if self.freq != NULL:
            LPBuffer.destroy(self.freq)
        if self.ratio != NULL:
            LPBuffer.destroy(self.ratio)
        if self.index != NULL:
            LPBuffer.destroy(self.index)
        if self.amp != NULL:
            LPBuffer.destroy(self.amp)
        if self.carrier != NULL:
            LPBuffer.destroy(self.carrier)
        if self.modulator != NULL:
            LPBuffer.destroy(self.modulator)

#@cython.freelist(32)
cdef class Osc:
    """ simple wavetable osc with linear interpolation
    """
    def __cinit__(
            self, 
            object wavetable=None, 
            object freq=440.0, 
            object amp=1.0,
            object pm=0.0,
            double phase=0, 

            object freq_interpolator=None,

            int wtsize=4096,
            int channels=DEFAULT_CHANNELS,
            int samplerate=DEFAULT_SAMPLERATE,

            int quality = 0
        ):

        self.freq = to_wavetable(freq, self.wtsize)
        self.amp = to_window(amp, self.wtsize)
        self.pm = to_wavetable(pm, self.wtsize)

        if freq_interpolator is None:
            freq_interpolator = 'linear'

        #self.freq_interpolator = interpolation.get_point_interpolator(freq_interpolator)

        self.wt_phase = phase
        self.freq_phase = 0
        self.amp_phase = 0
        self.pm_phase = 0

        self.channels = channels
        self.samplerate = samplerate
        self.wtsize = wtsize

        self.wavetable = to_wavetable(wavetable, self.wtsize)

        #if (quality > 0):
        #    self.bl_data = interpolation._bli_init(quality, True)
        #    self.interp_method = interpolation._bli_point
        #else:
        #    self.bl_data = interpolation._bli_init(1, True)
        #    self.interp_method = _linear_point_osc
        self.bl_data = LPInterpolation.bli_create(quality, 1)

    def play(Osc self, double length):
        cdef size_t framelength = <size_t>(length * self.samplerate)

        cdef size_t i = 0
        cdef double sample, freq, amp, pm
        cdef double lastpm = 0
        cdef double ilength = 1.0 / length

        cdef size_t freq_boundry = <size_t>max(self.freq.length, <size_t>1)
        cdef size_t amp_boundry = <size_t>max(self.amp.length, <size_t>1)
        cdef size_t wt_boundry = <size_t>max(self.wavetable.length, <size_t>1)
        cdef size_t pm_boundry = <size_t>max(self.pm.length, <size_t>1)

        self.bl_data.table_length = wt_boundry

        cdef double freq_phase_inc = ilength * freq_boundry
        cdef double amp_phase_inc = ilength * amp_boundry
        cdef double pm_phase_inc = ilength * pm_boundry

        cdef double wt_phase_inc = (1.0 / self.samplerate) * self.wtsize

        cdef lpbuffer_t * out = LPBuffer.create(framelength, self.channels, self.samplerate)

        cdef double last_inc = 1

        for i in range(framelength):
            #freq = self.freq_interpolator(self.freq, self.freq_phase)
            freq = LPInterpolation.linear(self.freq, self.freq_phase)
            amp = LPInterpolation.linear(self.amp, self.amp_phase)
            pm = LPInterpolation.linear(self.pm, self.pm_phase)
            if last_inc < 1: last_inc = 1
            self.bl_data.resampling_factor = abs(1/last_inc)
            sample = LPInterpolation.bli(self.bl_data, self.wavetable, self.wt_phase) * amp
            #sample = self.interp_method(self.wavetable, self.wt_phase, self.bl_data) * amp

            self.freq_phase += freq_phase_inc
            self.amp_phase += amp_phase_inc
            self.pm_phase += pm_phase_inc
            last_inc = freq * wt_phase_inc
            last_inc += (pm - lastpm) * wt_boundry * .5
            lastpm = pm
            self.wt_phase += last_inc

            if self.wt_phase < 0:
                self.wt_phase += wt_boundry
            elif self.wt_phase >= wt_boundry:
                self.wt_phase -= wt_boundry

            while self.amp_phase >= amp_boundry:
                self.amp_phase -= amp_boundry

            while self.freq_phase >= freq_boundry:
                self.freq_phase -= freq_boundry

            while self.pm_phase >= pm_boundry:
                self.pm_phase -= pm_boundry

            for channel in range(self.channels):
                out.data[i * self.channels + channel] = sample

        return SoundBuffer._fromlpbuffer(out)

    def __dealloc__(self):
        if self.freq != NULL:
            LPBuffer.destroy(self.freq)
        if self.amp != NULL:
            LPBuffer.destroy(self.amp)
        if self.wavetable != NULL:
            LPBuffer.destroy(self.wavetable)
        if self.pm != NULL:
            LPBuffer.destroy(self.pm)
        if self.bl_data != NULL:
            LPInterpolation.bli_destroy(self.bl_data)


#@cython.freelist(32)
cdef class Pulsar2d:
    """ Pulsar synthesis with a 2d wavetable & window stack
    """
    def __cinit__(
            self, 
            object wavetables=None, 
            object windows=None, 

            object freq=440.0, 
            object pulsewidth=1,
            object amp=1.0, 
            double phase=0, 

            object freq_interpolator=None,

            object wt_mod=None, 
            object win_mod=None, 

            object burst=None,
            object mask=1,

            int channels=DEFAULT_CHANNELS,
            int samplerate=DEFAULT_SAMPLERATE,
        ):

        if wt_mod is None:
            wt_mod = 'saw'

        if win_mod is None:
            win_mod = 'saw'

        if freq_interpolator is None:
            freq_interpolator = 'linear'

        self.osc = LPPulsarOsc.create()
        self.freq = to_wavetable(freq)
        self.amp = to_window(amp)
        self.wt_mod = to_window(wt_mod)
        self.win_mod = to_window(win_mod)
        self.mask = to_window(mask)

        #self.freq_interpolator = interpolation.get_point_interpolator(freq_interpolator)

        if burst is not None:
            self.burst_length = len(burst)
            self.burst = np.array(burst, dtype='long')
        else:
            self.burst_length = 1
            self.burst = np.array([1], dtype='long')

        self.wt_phase = phase
        self.win_phase = 0
        self.freq_phase = 0
        self.pw_phase = 0
        self.amp_phase = 0
        self.burst_phase = 0
        self.mask_phase = 0

        self.channels = channels
        self.samplerate = samplerate

        self.pulsewidth = to_wavetable(pulsewidth)

        cdef lpbuffer_t * wt
        cdef lpbuffer_t * win
        cdef double val
        cdef int i
        cdef int j

        if wavetables is None or len(wavetables) == 0:
            wavetables = ['sine']

        for wavetable in wavetables:
            wt = to_wavetable(wavetable, self.wt_length)
            LPPulsarOsc.add_wavetable(self.osc, wt)
            LPBuffer.destroy(wt)

        if windows is None or len(windows) == 0:
            windows = ['sine']

        for window in windows:
            win = to_window(window, self.win_length)
            LPPulsarOsc.add_window(self.osc, win)
            LPBuffer.destroy(win)

    def __dealloc__(self):
        if self.freq != NULL:
            LPBuffer.destroy(self.freq)
        if self.amp != NULL:
            LPBuffer.destroy(self.amp)
        if self.pulsewidth != NULL:
            LPBuffer.destroy(self.pulsewidth)
        if self.wt_mod != NULL:
            LPBuffer.destroy(self.wt_mod)
        if self.win_mod != NULL:
            LPBuffer.destroy(self.win_mod)
        if self.mask != NULL:
            LPBuffer.destroy(self.mask)
        if self.osc != NULL:
            LPPulsarOsc.destroy(self.osc)

    def add_wavetable(self, object wt):
        cdef lpbuffer_t * _wt = to_wavetable(wt)
        LPPulsarOsc.add_wavetable(self.osc, _wt)
        LPBuffer.destroy(_wt)

    def add_window(self, object win):
        cdef lpbuffer_t * _win = to_window(win)
        LPPulsarOsc.add_window(self.osc, _win)
        LPBuffer.destroy(_win)

    def play(self, length):
        cdef size_t framelength = <size_t>(length * self.samplerate)
        cdef size_t i = 0
        cdef lpfloat_t sample, pos, amp

        cdef lpbuffer_t * out = LPBuffer.create(framelength, self.channels, self.samplerate)

        self.osc.freq = LPInterpolation.linear_pos(self.freq, 0)
        self.osc.pulsewidth = LPInterpolation.linear_pos(self.pulsewidth, 0)
        self.osc.saturation = LPInterpolation.linear_pos(self.mask, 0)

        for i in range(framelength):
            pos = <lpfloat_t>i/framelength
            amp = LPInterpolation.linear_pos(self.amp, pos)
            sample = LPPulsarOsc.process(self.osc) * amp
            if self.osc.pulse_edge == 1:
                self.osc.freq = LPInterpolation.linear_pos(self.freq, pos)
                self.osc.pulsewidth = LPInterpolation.linear_pos(self.pulsewidth, pos)
                self.osc.saturation = LPInterpolation.linear_pos(self.mask, pos)
                #self.osc.wavetable_morph_freq = LPInterpolation.linear_pos(self.wt_mod, pos)
                #self.osc.window_morph_freq = LPInterpolation.linear_pos(self.win_mod, pos)

            for channel in range(self.channels):
                out.data[i * self.channels + channel] = sample

        return SoundBuffer._fromlpbuffer(out)

#@cython.freelist(32)
cdef class DelayLine:
    def __init__(self, int length):
        self.buf = np.zeros(length, dtype='int16')
        self.position = 0

#@cython.freelist(32)
cdef class Pluck:
    """ This is a port of Julius O Smith's `pluck.c` -- an implementation of digital waveguide synthesis.
        I've tried to preserve his original comments inline.

        The original can be found here: https://ccrma.stanford.edu/~jos/pmudw/pluck.c

        pluck.c - elementary waveguide simulation of plucked strings - JOS 6/6/92
    """
    def __init__(self, double freq=220.0, double pick=0.1, double pickup=0.2, double amp=1, object seed=None, int samplerate=44100, int channels=2):
        cdef int i
        self.state = 0
        self.freq = freq
        self.pick = pick
        self.pickup = pickup
        self.amp = amp
        self.samplerate = samplerate
        self.channels = channels

        self.rail_length = <int>(<double>samplerate / freq / 2.0 + 1.0)

        self.upper_rail = DelayLine(self.rail_length)
        self.lower_rail = DelayLine(self.rail_length)

        # Round pick position to nearest spatial sample.
        # A pick position at x = 0 is not allowed.
        cdef int pickSample = <int>max(self.rail_length * pick, 1)
        cdef double upslope = <double>pickSample
        cdef double downslope = <double>(self.rail_length - pickSample - 1)

        if seed is None:
            self.seed = LPBuffer.create(self.rail_length, 1, samplerate)

            for i in range(pickSample):
                self.seed.data[i] = upslope * i

            for i in range(pickSample, self.rail_length):
                self.seed.data[i] = downslope * (self.rail_length - 1 - i)
        else:
            self.seed = to_window(seed, self.rail_length)

        # FIXME
        #self.seed = np.interp(self.seed, (np.max(self.seed), np.min(self.seed)), (0, amp))

        # Initial conditions for the ideal plucked string.
        # "Past history" is measured backward from the end of the array.
        for i in range(self.rail_length):
            self.lower_rail.buf[i] = DOUBLE_TO_SHORT(0.5 * self.seed.data[i])

        for i in range(self.rail_length):
            self.upper_rail.buf[i] = DOUBLE_TO_SHORT(0.5 * self.seed.data[i])

        self.pickup_location = <int>(self.pickup * self.rail_length)

    cpdef short get_sample(Pluck self, DelayLine dline, int position):
        return dline.buf[(dline.position + position) % self.rail_length]

    cpdef double next_sample(Pluck self):
        cdef short yp0, ym0, ypM, ymM
        cdef short outsamp, outsamp1

        # Output at pickup location 
        # Returns spatial sample at location "position", where position zero
        # is equal to the current upper delay-line pointer position (x = 0).
        # In a right-going delay-line, position increases to the right, and
        # delay increases to the right => left = past and right = future.

        # Returns sample "position" samples into delay-line's past.
        # Position "0" points to the most recently inserted sample.
        outsamp = self.get_sample(self.upper_rail, self.pickup_location)

        # Returns spatial sample at location "position", where position zero
        # is equal to the current lower delay-line pointer position (x = 0).
        # In a left-going delay-line, position increases to the right, and
        # delay DEcreases to the right => left = future and right = past.
        outsamp1 = self.get_sample(self.lower_rail, self.pickup_location)

        outsamp += outsamp1

        ym0 = self.get_sample(self.lower_rail, 1) # Sample traveling into "bridge"
        ypM = self.get_sample(self.upper_rail, self.rail_length - 2) # Sample to "nut"

        ymM = -ypM                    # Inverting reflection at rigid nut 

        # Implement a one-pole lowpass with feedback coefficient = 0.5 
        # outsamp = 0.5 * outsamp + 0.5 * insamp 
        self.state = (self.state >> 1) + (ym0 >> 1)

        yp0 = -self.state  # Reflection at yielding bridge 

        # String state update 

        # Decrements current upper delay-line pointer position (i.e.
        # the wave travels one sample to the right), moving it to the
        # "effective" x = 0 position for the next iteration.  The
        # "bridge-reflected" sample from lower delay-line is then placed
        # into this position.

        # Decrement pointer and then update 
        self.upper_rail.position -= 1
        self.upper_rail.buf[self.upper_rail.position % self.rail_length] = yp0

        # Places "nut-reflected" sample from upper delay-line into
        # current lower delay-line pointer location (which represents
        # x = 0 position).  The pointer is then incremented (i.e. the
        # wave travels one sample to the left), turning the previous
        # position into an "effective" x = L position for the next
        # iteration.

        # Update and then increment pointer
        self.lower_rail.buf[self.lower_rail.position % self.rail_length] = ymM
        self.lower_rail.position += 1

        return <double>(outsamp / 32768.0) * self.amp


    cpdef SoundBuffer play(Pluck self, double length, object seed=None):
        cdef size_t i=0, framelength = <size_t>(length * self.samplerate)
        cdef int c
        cdef lpbuffer_t * out = LPBuffer.create(framelength, self.channels, self.samplerate)
        cdef lpbuffer_t * _seed
        cdef lpfloat_t sample = 0

        if seed is not None:
            _seed = to_window(seed, self.rail_length)

            for i in range(<size_t>self.rail_length):
                self.lower_rail.buf[i] += DOUBLE_TO_SHORT(0.5 * _seed.data[i])

            for i in range(<size_t>self.rail_length):
                self.upper_rail.buf[i] += DOUBLE_TO_SHORT(0.5 * _seed.data[i])

            LPBuffer.destroy(_seed)

        for i in range(framelength):
            sample = self.next_sample()
            for c in range(self.channels):
                out.data[i * self.channels + c] = sample

        return SoundBuffer._fromlpbuffer(out)

    def __dealloc__(self):
        if self.seed != NULL:
            LPBuffer.destroy(self.seed)


#@cython.freelist(32)
cdef class SineOsc:
    """ simple wavetable osc with linear interpolation
    """
    def __cinit__(
            self, 
            object freq=440.0, 
            object amp=1.0, 
            double phase=0, 

            object freq_interpolator=None,

            int wtsize=4096,
            int channels=DEFAULT_CHANNELS,
            int samplerate=DEFAULT_SAMPLERATE,
        ):

        self.freq = to_wavetable(freq, self.wtsize)
        self.amp = to_window(amp, self.wtsize)

        #if freq_interpolator is None:
        #    freq_interpolator = 'linear'
        #self.freq_interpolator = interpolation.get_point_interpolator(freq_interpolator)

        self.osc_phase = phase
        self.freq_phase = phase
        self.amp_phase = phase

        self.channels = channels
        self.samplerate = samplerate
        self.wtsize = wtsize

    def play(self, length):
        cdef size_t framelength = <size_t>(length * self.samplerate)

        cdef size_t i = 0
        cdef double sample, freq, amp
        cdef double ilength = 1.0 / framelength
        cdef double isamplerate = 1.0 / self.samplerate
        cdef double PI2 = PI*2

        cdef size_t freq_boundry = <size_t>max(self.freq.length-1, <size_t>1)
        cdef size_t amp_boundry = <size_t>max(self.amp.length-1, <size_t>1)

        cdef double freq_phase_inc = ilength * freq_boundry
        cdef double amp_phase_inc = ilength * amp_boundry

        cdef lpbuffer_t * out = LPBuffer.create(framelength, self.channels, self.samplerate)

        for i in range(framelength):
            #freq = self.freq_interpolator(self.freq, self.freq_phase)
            freq = LPInterpolation.linear(self.freq, self.freq_phase)
            amp = LPInterpolation.linear(self.amp, self.amp_phase)
            sample = math.sin(PI2 * self.osc_phase) * amp

            self.freq_phase += freq_phase_inc
            self.amp_phase += amp_phase_inc
            self.osc_phase += freq * isamplerate

            while self.osc_phase >= 1:
                self.osc_phase -= 1

            while self.amp_phase >= amp_boundry:
                self.amp_phase -= amp_boundry

            while self.freq_phase >= freq_boundry:
                self.freq_phase -= freq_boundry

            for channel in range(self.channels):
                out.data[i * self.channels + channel] = sample

        return SoundBuffer._fromlpbuffer(out)

    def __dealloc__(self):
        if self.freq != NULL:
            LPBuffer.destroy(self.freq)
        if self.amp != NULL:
            LPBuffer.destroy(self.amp)


#@cython.freelist(32)
cdef class Tukey:
    def __cinit__(
            Tukey self, 
            object freq=440.0, 
            object shape=0.5,
            object amp=1.0, 
            double phase=0,            
            object freq_interpolator=None,

            int channels=DEFAULT_CHANNELS,
            int samplerate=DEFAULT_SAMPLERATE,
        ):

        self.phase = phase        
        self.channels = channels
        self.samplerate = samplerate

        if freq_interpolator is None:
            freq_interpolator = 'linear'

        if shape is None:
            shape = 'sine'

        self.amp = to_window(amp)
        self.shape = to_window(shape)
        self.freq = to_window(freq)
        #self.freq_interpolator = interpolation.get_pos_interpolator(freq_interpolator)

    cpdef SoundBuffer play(Tukey self, double length=1):
        cdef int c=0, i=0
        cdef double r=0, pos=0, sample=0, a=0, x=0, amp=1

        cdef long _length = <long>(length * self.samplerate)
        cdef lpbuffer_t * out = LPBuffer.create(_length, self.channels, self.samplerate)
        cdef int direction = 1
        cdef double PI2 = PI*2

        while i < _length:
            pos = <double>i / <double>_length
            amp = LPInterpolation.linear_pos(self.amp, pos)
            r = LPInterpolation.linear_pos(self.shape, pos)
            r = max(r, 0.00001)

            f = LPInterpolation.linear_pos(self.freq, pos)
            #f = self.freq_interpolator(self.freq, pos)

            a = PI2 / r

            # Implementation based on https://www.mathworks.com/help/signal/ref/tukeywin.html
            if self.phase <= r / 2:
                sample = 0.5 * (1 + math.cos(a * (self.phase - r / 2)))

            elif self.phase < 1 - (r/2):
                sample = 1

            else:
                sample = 0.5 * (1 + math.cos(a * (self.phase - 1 + r / 2)))

            sample *= direction

            for c in range(self.channels):
                out.data[i * self.channels + c] = sample * amp

            self.phase += (1.0/self.samplerate) * f * 2

            if self.phase > 1:
                direction *= -1
            while self.phase >= 1:
                self.phase -= 1

            i += 1

        return SoundBuffer._fromlpbuffer(out)

    def __dealloc__(self):
        if self.shape != NULL:
            LPBuffer.destroy(self.shape)
        if self.freq != NULL:
            LPBuffer.destroy(self.freq)
        if self.amp != NULL:
            LPBuffer.destroy(self.amp)

