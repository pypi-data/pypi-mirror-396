from os import path
import random
import shutil
import tempfile
from unittest import TestCase

from pippi.soundbuffer import SoundBuffer
from pippi import dsp, microsound, fx, shapes

class TestCloud(TestCase):
    def test_wavetable_implementation(self):
        sound = dsp.read('tests/sounds/noise1s.wav')
        out = sound.cloud(length=10, window='sine', grainlength=0.5, grid=1)
        out.write('tests/renders/graincloud_wavetable_placement.wav')

    def test_libpippi_graincloud(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        cloud = microsound.Formation(sound, speed=1)

        length = 60
        framelength = int(length * sound.samplerate)

        out = cloud.play(length)
        out = fx.norm(out, 1)

        out.write('tests/renders/graincloud_libpippi_unmodulated.wav')

        self.assertEqual(len(out), framelength)

    def test_libpippi_graincloud(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        cloud = microsound.Formation(sound, speed=1)

        length = 300
        framelength = int(length * sound.samplerate)

        out = cloud.play(length)
        out = fx.norm(out, 1)

        out.write('tests/renders/graincloud_libpippi_length_modulated.wav')

        self.assertEqual(len(out), framelength)

    """ FIXME this renders for ever and ever...
    def test_grainlength_modulation(self):
        snd = dsp.read('tests/sounds/living.wav')
        grainlength = shapes.win('sine', dsp.MS*100, 2)
        out = snd.cloud(snd.dur*2, grainlength=grainlength)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_grainlength_modulated.wav')
    """

    def test_user_window(self):
        snd = dsp.read('tests/sounds/living.wav')

        length = 30

        win = dsp.win('pluckout').taper(dsp.randint(10, 100))
        out = dsp.buffer(length=length, channels=snd.channels, samplerate=snd.samplerate)

        for _ in range(4):
            speed = shapes.win('sine', dsp.rand(0.125, 0.5), dsp.rand(1, 2))
            amp = shapes.win('sine', 0.3, 1) 
            spread = shapes.win('sine', 0, 1) 
            grid = shapes.win('sine', -1, 1, length=dsp.rand(1, 10))
            grainlength = shapes.win('sine', dsp.MS*1, 0.4, length=dsp.rand(1, 10))

            gridjitter = shapes.win('sine', 0, 1)
            grainjitter = shapes.win('sine', 0, 1)
            pulsewidth = shapes.win('sine', 0.5, 2)

            layer = snd.cloud(length, 
                amp=amp,
                window=win, 
                grainlength=grainlength, 
                numgrains=2, 
                speed=speed, 
                pulsewidth=pulsewidth, 
                spread=spread,
                gridincrement=True,
                grainmaxjitter=dsp.rand(0.01,10),
                grainjitter=grainjitter,
                gridmaxjitter=dsp.rand(0.01,1),
                gridjitter=gridjitter,
            )
            out.dub(layer)

        out = fx.compressor(out*8, -15, 15)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_user_window.wav')

    def test_offset_modulation(self):
        snd = dsp.read('tests/sounds/living.wav')
        out = snd.cloud(snd.dur*2, grainlength=0.1, offset=shapes.win('sine', 0, snd.dur))
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_offset_modulated.wav')

    def test_offset_fixed(self):
        snd = dsp.read('tests/sounds/living.wav')
        out = snd.cloud(snd.dur*2, grainlength=0.1, offset=dsp.rand(0.3, snd.dur))
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_offset_fixed.wav')

    def test_offset_unmodulated(self):
        snd = dsp.read('tests/sounds/living.wav')
        out = snd.cloud(snd.dur, grainlength=0.1)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_offset_unmodulated.wav')

    def test_speed_modulated(self):
        snd = dsp.read('tests/sounds/living.wav')
        speed = shapes.win('sine', 0.5, 2)
        out = snd.cloud(snd.dur, grainlength=0.1, speed=speed)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_speed_modulated.wav')

    def test_libpippi_pulsed_graincloud(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        out = sound.cloud(10, grainlength=0.06, grid=0.12)
        out.write('tests/renders/graincloud_libpippi_pulsed.wav')

    def test_libpippi_graincloud_with_length_lfo(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        grainlength = dsp.wt('hann', 0.01, 0.1)
        length = 3 
        framelength = int(length * sound.samplerate)

        out = sound.cloud(length, grainlength=grainlength)

        self.assertEqual(len(out), framelength)

        out.write('tests/renders/graincloud_libpippi_with_length_lfo.wav')

    def test_libpippi_graincloud_with_speed_lfo(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        minspeed = random.triangular(0.05, 1)
        maxspeed = minspeed + random.triangular(0.5, 10)
        speed = dsp.wt('rnd', minspeed, maxspeed)
        cloud = microsound.Formation(sound, grainlength=0.04, speed=speed)

        length = 3
        framelength = int(length * sound.samplerate)

        out = cloud.play(length)
        self.assertEqual(len(out), framelength)

        out.write('tests/renders/graincloud_libpippi_with_speed_lfo.wav')

    def test_libpippi_graincloud_with_extreme_speed_lfo(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')

        length = 3
        speed = dsp.wt('hann', 1, 100)
        framelength = int(length * sound.samplerate)

        out = sound.cloud(length=length, speed=speed)
        self.assertEqual(len(out), framelength)

        out.write('tests/renders/graincloud_libpippi_with_extreme_speed_lfo.wav')

    def test_libpippi_graincloud_with_read_lfo(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        #cloud = microsound.Formation(sound, position=dsp.win('hann', 0, 1))
        cloud = microsound.Formation(sound, position='hann')

        length = 3
        out = cloud.play(length)
        self.assertEqual(out.dur, length)

        out.write('tests/renders/graincloud_libpippi_with_read_lfo.wav')

    def test_libpippi_graincloud_grainsize(self):
        snd = dsp.read('tests/sounds/living.wav')
        out = snd.cloud(
                length=dsp.rand(8, 16), 
                window='hann', 
                grainlength=dsp.win('sinc', 0.2, 6), 
                grid=dsp.win('hannout', 0.04, 1),
                spread=1, 
            )

        out.write('tests/renders/graincloud_libpippi_grainsize.wav')

    def test_grid_modulation_linear(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        # Linear sweep from fast grains (10ms) to slow grains (200ms)
        grid = shapes.win('line', 0.01, 0.2)
        cloud = microsound.Formation(sound, grainlength=0.05, grid=grid)
        
        length = 5
        out = cloud.play(length)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_grid_linear.wav')

    def test_grid_modulation_sine(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        # Sine wave modulation between 25ms and 100ms intervals
        grid = shapes.win('sine', 0.025, 0.1)
        cloud = microsound.Formation(sound, grainlength=0.08, grid=grid)
        
        length = 4
        out = cloud.play(length)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_grid_sine.wav')

    def test_grid_modulation_step(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        # Step changes in grid timing
        grid_values = [0.05, 0.15, 0.03, 0.12, 0.08]
        grid = shapes.win(grid_values)
        cloud = microsound.Formation(sound, grainlength=0.06, grid=grid)
        
        length = 3
        out = cloud.play(length)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_grid_step.wav')

    """
    def test_grid_modulation_extreme(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        # Extreme modulation from very fast to very slow
        grid = shapes.win('hann', 0.005, 0.5)
        cloud = microsound.Formation(sound, grainlength=0.1, grid=grid)
        
        length = 6
        out = cloud.play(length)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_grid_extreme.wav')

    def test_grid_and_grainlength_modulation(self):
        sound = SoundBuffer(filename='tests/sounds/living.wav')
        # Modulate both grid and grainlength together
        grid = shapes.win('sine', 0.02, 0.15)
        grainlength = shapes.win('sine', 0.03, 0.12)
        cloud = microsound.Formation(sound, grainlength=grainlength, grid=grid)
        
        length = 4
        out = cloud.play(length)
        out = fx.norm(out, 1)
        out.write('tests/renders/graincloud_libpippi_grid_and_length.wav')
    """

