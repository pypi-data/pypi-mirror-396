cimport cython

from pippi.soundbuffer cimport SoundBuffer, to_window

#@cython.freelist(32)
cdef class Formation:
    def __cinit__(self, 
            SoundBuffer snd, 
            object window=None, 
            object position=None,
            object amp=1.0,
            object speed=1.0, 
            object spread=0.0, 
            object pulsewidth=1.0,
            object grainmaxjitter=0.5, 
            object grainjitter=0.0, 
            object grainlength=0.1, 
            object gridmaxjitter=0.5, 
            object gridjitter=0.0, 
            object grid=None,
            object mask=None,
            object offset=None,
            int numgrains=2,
            unsigned int wtsize=4096,
            bint gridincrement=False,
            bint onsets=False
        ):

        #print(f'{grainlength=}')

        cdef double grain_length_scalar = 0.1
        self.channels = snd.channels
        self.samplerate = snd.samplerate
        self.grainlength = to_window(grainlength)
        #print(f'{self.grainlength.length=}')
        #print(f'{self.grainlength.data[1]=}')
        self.grainlength.data[0] = self.grainlength.data[1]

        self.onsets = [0]
        self.track_onsets = onsets

        if window is None:
            window = 'hann'

        if position is None:
            position = 'phasor'

        if grid is None:
            grid = self.grainlength.data[0] * 0.5

        if offset is None:
            self.offset = NULL
        else:
            self.offset = to_window(offset)

        self.win = to_window(window)
        self.grid = to_window(grid)
        self.amp = to_window(amp)
        self.speed = to_window(speed)
        self.spread = to_window(spread)
        self.position = to_window(position)
        self.pulsewidth = to_window(pulsewidth)
        self.gridmaxjitter = to_window(gridmaxjitter)
        self.gridjitter = to_window(gridjitter)
        self.grainmaxjitter = to_window(grainmaxjitter)
        self.grainjitter = to_window(grainjitter)
        self.gridincrement = gridincrement

        self.formation = LPFormation.create(snd.buffer, self.win)

    def __dealloc__(self):
        if self.formation != NULL:
            LPBuffer.destroy(self.win)
            LPBuffer.destroy(self.grid)
            LPBuffer.destroy(self.amp)
            LPBuffer.destroy(self.offset)
            LPBuffer.destroy(self.speed)
            LPBuffer.destroy(self.spread)
            LPBuffer.destroy(self.position)
            LPBuffer.destroy(self.pulsewidth)
            LPBuffer.destroy(self.gridmaxjitter)
            LPBuffer.destroy(self.gridjitter)
            LPBuffer.destroy(self.grainmaxjitter)
            LPBuffer.destroy(self.grainjitter)
            LPBuffer.destroy(self.grainlength)
            LPFormation.destroy(self.formation)

    def play(self, double length):
        cdef size_t i, c, framelength
        cdef lpfloat_t pos=0, amp=1, offset=0
        cdef lpbuffer_t * out

        # init params and prime the first grain
        LPFormation.update_interval(self.formation, LPInterpolation.linear_pos(self.grid, pos))
        self.formation.pulsewidth = LPInterpolation.linear_pos(self.pulsewidth, pos)
        self.formation.grainlength = LPInterpolation.linear_pos(self.grainlength, pos)
        self.formation.grainlength_jitter = LPInterpolation.linear_pos(self.grainjitter, pos)
        self.formation.grainlength_maxjitter = LPInterpolation.linear_pos(self.grainmaxjitter, pos)
        self.formation.speed = LPInterpolation.linear_pos(self.speed, pos)
        self.formation.spread = LPInterpolation.linear_pos(self.spread, pos)
        self.formation.grid_jitter = LPInterpolation.linear_pos(self.gridjitter, pos)
        self.formation.grid_maxjitter = LPInterpolation.linear_pos(self.gridmaxjitter, pos)
        if self.offset != NULL:
            self.formation.offset = <size_t>(LPInterpolation.linear_pos(self.offset, pos) * self.samplerate)
        LPFormation.init(self.formation)

        framelength = <size_t>(length * self.samplerate)
        
        out = LPBuffer.create(framelength, self.channels, self.samplerate)
        #print(f'f grainlength {self.formation.grainlength=}')

        for i in range(framelength):
            pos = LPInterpolation.linear_pos(self.position, i / <double>framelength)
            amp = LPInterpolation.linear_pos(self.amp, pos)

            self.formation.pulsewidth = LPInterpolation.linear_pos(self.pulsewidth, pos)
            self.formation.grainlength = LPInterpolation.linear_pos(self.grainlength, pos)
            #print(f'{i=} {pos=} f grainlength {self.formation.grainlength=}')
            self.formation.grainlength_jitter = LPInterpolation.linear_pos(self.grainjitter, pos)
            self.formation.grainlength_maxjitter = LPInterpolation.linear_pos(self.grainmaxjitter, pos)
            self.formation.speed = LPInterpolation.linear_pos(self.speed, pos)
            self.formation.spread = LPInterpolation.linear_pos(self.spread, pos)
            self.formation.grid_jitter = LPInterpolation.linear_pos(self.gridjitter, pos)
            self.formation.grid_maxjitter = LPInterpolation.linear_pos(self.gridmaxjitter, pos)

            LPFormation.update_interval(self.formation, LPInterpolation.linear_pos(self.grid, pos))
            LPFormation.process(self.formation)

            if self.formation.gate == 1:
                #print(f'f grainlength {self.formation.grainlength=}')
                if self.track_onsets:
                    self.onsets += [ i/<lpfloat_t>self.samplerate ]

                if self.offset == NULL:
                    LPFormation.increment_offset(self.formation)
                else:
                    self.formation.offset = <size_t>(LPInterpolation.linear_pos(self.offset, pos) * self.samplerate)

            for c in range(self.channels):
                out.data[i * self.channels + c] = self.formation.current_frame.data[c] * amp

        if self.track_onsets:
            return SoundBuffer._fromlpbuffer(out), self.onsets

        else:
            return SoundBuffer._fromlpbuffer(out)
