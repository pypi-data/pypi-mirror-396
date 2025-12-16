import random
from unittest import TestCase

from pippi.oscs import Pulsar2d
from pippi.soundbuffer import SoundBuffer
from pippi import dsp, fx, tune, shapes

import numpy as np

class TestOscs(TestCase):
    def test_create_pulsar2d(self):
        osc = Pulsar2d(
                ['sine', 'square', 'tri', 'sine'], 
                windows=['sine', 'tri', 'hann'], 
                wt_mod=dsp.wt('saw', 0, 1), 
                win_mod=dsp.wt('rsaw', 0, 1), 
                pulsewidth=dsp.wt('tri', 0, 1), 
                freq=200.0, 
                amp=0.2
            )
        length = 10
        out = osc.play(length)
        out.write('tests/renders/osc_pulsar2d.wav')
        self.assertEqual(len(out), int(length * out.samplerate))

    def test_pulsar2d_burst(self):
        osc = Pulsar2d(
                ['sine'], 
                windows=['sine'], 
                pulsewidth=dsp.wt('tri', 0, 1), 
                burst=(3,2),
                freq=200.0, 
                amp=0.2
            )
        length = 10
        out = osc.play(length)
        out.write('tests/renders/osc_pulsar2d_burst.wav')
        self.assertEqual(len(out), int(length * out.samplerate))

    def test_pulsar2d_mask(self):
        osc = Pulsar2d(
                ['sine'], 
                windows=['sine'], 
                pulsewidth=dsp.wt('tri', 0, 1), 
                mask=dsp.wt('phasor', 0, 1), 
                freq=200.0, 
                amp=0.2
            )
        length = 10
        out = osc.play(length)
        out.write('tests/renders/osc_pulsar2d_mask.wav')
        self.assertEqual(len(out), int(length * out.samplerate))

    def test_pulsar2d_burst_and_mask(self):
        osc = Pulsar2d(
                ['sine'], 
                windows=['sine'], 
                pulsewidth=dsp.wt('tri', 0, 1), 
                mask=dsp.randline(30, 0, 1), 
                burst=(3,2),
                freq=200.0, 
                amp=0.2
            )
        length = 10
        out = osc.play(length)
        out.write('tests/renders/osc_pulsar2d_burst_and_mask.wav')
        self.assertEqual(len(out), int(length * out.samplerate))

    def test_waveset_pulsar2d(self):
        rain = dsp.read('tests/sounds/rain.wav').cut(0, 1)
        ws = dsp.ws(rain)
        ws = dsp.apply(ws, lambda s: fx.norm(s, 1))
        osc = Pulsar2d(ws,
                windows=['sine'], 
                freq=200.0, 
                amp=0.2
            )
        out = osc.play(10)
        out.write('tests/renders/osc_waveset_pulsar2d.wav')

    def test_freq_interpolation_pulsar2d(self):
        freqs = tune.degrees([1,3,5,9,2,4,6,5,1], octave=3, key='a') * 10
        out = Pulsar2d(['sine', 'tri', 'square', 'hann'], ['hann'], 
            freq=freqs, 
            freq_interpolator='trunc',
            amp=0.2
        ).play(10)
        out.write('tests/renders/osc_pulsar2d_freq_trunc.wav')

    def test_another_ws(self):
        fizz = dsp.read('tests/sounds/rain.wav')

        freqs = tune.chord('I', octave=dsp.randint(1,5), key='g')
        freq = dsp.choice(freqs)
        speed = freq / 579.0
        length = dsp.rand(0.3, 3)

        out = fizz.rcut(length * (1/speed))
        out = out.env('sineout').taper(dsp.MS * dsp.rand(10, 20))

        ws = dsp.ws(out, offset=dsp.randint(0, 1000), modulo=3, limit=10)
        ws = dsp.apply(ws, lambda s: fx.norm(s, 1))

        out = out.speed(speed)
        out = fx.hpf(out, freq - 10)

        tone = Pulsar2d(ws, freq=freq).play(length).env('rnd') * dsp.rand(0.5, 1)

        out = out.env(tone)
        out.dub(tone * dsp.rand(0.25, 0.5))

        #out = fx.fold(out, dsp.rand(1, 3))

        out = out.env('rnd')
        out = fx.compressor(out * 10, -15, 15)
        out = fx.norm(out, dsp.rand(0.5, 0.75))
        out.write('tests/renders/osc_pulsar2d_another_ws.wav')

