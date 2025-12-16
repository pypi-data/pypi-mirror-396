import random
from unittest import TestCase

from pippi.oscs import Pulsar2d
from pippi.soundbuffer import SoundBuffer
from pippi import dsp, fx, wavesets

class TestSoundBuffers(TestCase):
    def test_pulsar_from_waveset(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        waveset = dsp.ws(sound, limit=20, modulo=1)
        waveset = dsp.apply(waveset, lambda s: fx.norm(s, 1))
        osc = Pulsar2d(
                waveset,
                windows=['sine'], 
                wt_mod=dsp.wt('saw', 0, 1), 
                win_mod=0.0, 
                pulsewidth=1.0, 
                freq=80.0, 
                amp=0.8
            )

        length = 30
        out = osc.play(length)
        out.write('tests/renders/waveset_pulsar2d_wavetables-80hz.wav')
        self.assertEqual(len(out), int(length * out.samplerate))

    def test_interleave(self):
        sound1 = SoundBuffer(filename='tests/sounds/linux.wav')
        sound2 = SoundBuffer(filename='tests/sounds/guitar10s.wav')
        waveset1 = dsp.ws(sound1, limit=10, offset=1000)
        waveset2 = dsp.ws(sound2, limit=10, offset=1000)

        waveset = wavesets.interleave(waveset1, waveset2)

        out = dsp.join(waveset)
        out.write('tests/renders/waveset_interleave.wav')

    def test_stretch(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        waveset = dsp.ws(sound)
        factor = dsp.wt('phasor', 1, 10)
        out = wavesets.stretch(waveset, factor)
        out = dsp.join(waveset)
        out.write('tests/renders/waveset_stretch.wav')

    """
    def test_harmonic(self):
        sound = SoundBuffer(filename='tests/sounds/guitar10s.wav')
        waveset = SoundBuffer(sound)
        harmonics = [1, 2, 3]
        weights = [1, 0.5, 0.25]
        out = waveset.harmonic(harmonics, weights)
        out.write('tests/renders/waveset_harmonic_distortion.wav')

    def test_substitute(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        waveset = SoundBuffer(sound)
        out = waveset.substitute('sine')
        out = dsp.join(waveset)
        out.write('tests/renders/waveset_substitute_sine.wav')

    def test_substitute_reversed(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        waveset = SoundBuffer(sound)
        rev = waveset.reversed()
        out = waveset.replace(rev)
        out = fx.norm(out, 1)
        out.write('tests/renders/waveset_substitute_reversed.wav')
    """

    def test_reverse(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        waveset = dsp.ws(sound)
        waveset.reverse()
        waveset = dsp.apply(waveset, lambda s: s.reversed())
        out = dsp.join(waveset)
        out.write('tests/renders/waveset_reverse.wav')

    def test_normalize(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        waveset = dsp.ws(sound)
        waveset = dsp.apply(waveset, lambda s: fx.norm(s, 1))
        out = dsp.join(waveset)
        out.write('tests/renders/waveset_normalize.wav')

    def test_retrograde(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        for crossings in [3,30,100,300]:
            waveset = dsp.ws(sound, crossings=crossings)
            out = wavesets.retrograde(waveset)
            out = dsp.join(waveset)
            out.write('tests/renders/waveset_retrograde_%s_crossings.wav' % crossings)

    """
    def test_morph(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        tsound = SoundBuffer(filename='tests/sounds/guitar10s.wav')
        waveset = SoundBuffer(sound)
        target = SoundBuffer(tsound)
        out = waveset.morph(target, 'phasor')
        out.write('tests/renders/waveset_morph_phasor.wav')
    """

    def test_render(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        waveset = dsp.ws(sound)
        out = dsp.join(waveset)
        out.write('tests/renders/waveset_render.wav')

        self.assertEqual(len(out), len(sound))

