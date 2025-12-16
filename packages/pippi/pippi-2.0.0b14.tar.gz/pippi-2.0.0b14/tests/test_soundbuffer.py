from os import path
import random
import shutil
import tempfile
from unittest import TestCase

from pippi.soundbuffer import SoundBuffer
from pippi import dsp, fx

DEFAULT_SAMPLERATE = 48000
TEST_SAMPLERATE = 44100

class TestSoundBuffer(TestCase):
    def setUp(self):
        self.soundfiles = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.soundfiles)

    def test_create_empty_buffer(self):
        sound = SoundBuffer()
        self.assertTrue(len(sound) == 0)
        self.assertTrue(not sound)

        sound = SoundBuffer(length=1)
        self.assertEqual(len(sound), DEFAULT_SAMPLERATE)
        self.assertTrue(sound)

    def test_diff(self):
        snd = SoundBuffer(filename='tests/sounds/guitar10s.wav')
        snd_b = fx.crush(snd)
        out = snd.diff(snd_b)
        out.write('tests/renders/soundbuffer_diff.wav')
        out = snd_b.diff(snd)
        out.write('tests/renders/soundbuffer_diff_reverse.wav')

    def test_fadeout(self):
        snd = SoundBuffer(filename='tests/sounds/guitar10s.wav')
        snd.fadeout(0).write('tests/renders/soundbuffer_fadeout_0.0.wav')
        snd.fadeout(0.5).write('tests/renders/soundbuffer_fadeout_0.5.wav')
        snd.fadeout(1).write('tests/renders/soundbuffer_fadeout_1.0.wav')

    def test_mix_operator(self):
        snd1 = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        snd2 = SoundBuffer(filename='tests/sounds/LittleTikes-A1.wav')

        snd1 &= snd2

        self.assertEqual(snd1.dur, snd2.dur)

    # FIXME: Implement channel mapping support in remix() method
    # def test_swap_channels(self):
    #     snd = SoundBuffer(filename='tests/sounds/LittleTikes-A1.wav')
    #     snd = snd.remix([2,1])
    #     snd.write('tests/renders/soundbuffer_swap_channels.wav')

    def test_mix_mismatched_channels(self):
        snd1 = SoundBuffer(filename='tests/sounds/guitar1s.wav').remix(1)
        snd2 = SoundBuffer(filename='tests/sounds/LittleTikes-A1.wav')
        channels = max(snd1.channels, snd2.channels)

        out = snd1 & snd2
        self.assertEqual(out.channels, channels)

        out = snd2 & snd1
        self.assertEqual(out.channels, channels)

        snd2 &= snd1
        self.assertEqual(snd2.channels, channels)
        self.assertEqual(snd1.channels, 1) # Right side should have no side effects

        snd1 &= snd2
        self.assertEqual(snd1.channels, channels)

    def test_create_stereo_buffer_from_soundfile(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        self.assertEqual(len(sound), sound.samplerate)
        self.assertTrue(sound.samplerate == 44100)

        sound = dsp.read('tests/sounds/guitar1s.wav')
        self.assertEqual(len(sound), sound.samplerate)
        self.assertTrue(sound.samplerate == 44100)

    def test_graph_soundfile(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        sound.graph('tests/renders/graph_soundbuffer.png', width=1280, height=800)

    def test_create_mono_buffer_from_soundfile(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        self.assertTrue(sound.samplerate == TEST_SAMPLERATE)
        self.assertTrue(sound.channels == 1)
        self.assertEqual(len(sound), 228554)

        sound = dsp.read('tests/sounds/linux.wav')
        self.assertTrue(sound.samplerate == TEST_SAMPLERATE)
        self.assertTrue(sound.channels == 1)
        self.assertEqual(len(sound), 228554)

    def test_create_mono_buffer_from_wavetable(self):
        wt = dsp.wt('sine', wtsize=4096)
        self.assertTrue(len(wt) == 4096)

        snd = dsp.buffer(wt)
        self.assertTrue(len(snd) == 4096)
        self.assertTrue(snd[100] != 0)

        snd = SoundBuffer(wt)
        self.assertTrue(len(snd) == 4096)
        self.assertTrue(snd[100] != 0)

    def test_stack_soundbuffer(self):
        snd1 = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        snd2 = SoundBuffer(filename='tests/sounds/LittleTikes-A1.wav')
        channels = snd1.channels + snd2.channels
        length = max(len(snd1), len(snd2))
        out = dsp.stack([snd1, snd2])
        self.assertTrue(channels == out.channels)
        self.assertTrue(length == len(out))
        self.assertTrue(snd1.samplerate == out.samplerate)
        out.write('tests/renders/soundbuffer_stack.wav')

    def test_convolve_soundbuffer(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')

        impulse = SoundBuffer(filename='tests/sounds/LittleTikes-A1.wav')
        out = sound.convolve(impulse)
        out.write('tests/renders/soundbuffer_convolve_guitar_littletikes.wav')

        impulse = SoundBuffer(dsp.win('sinc'), channels=sound.channels, samplerate=sound.samplerate)
        out = sound.convolve(impulse)
        out.write('tests/renders/soundbuffer_convolve_guitar_sinc.wav')

    def test_clip_soundbuffer(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')

        sound = sound.clip(-0.1, 0.1)

        self.assertEqual(len(sound), TEST_SAMPLERATE)
        self.assertTrue(sound.samplerate == TEST_SAMPLERATE)
        self.assertTrue(sound.max <= 0.1)

    def test_save_buffer_to_soundfile(self):
        filename = path.join(self.soundfiles, 'test_save_buffer_to_soundfile.{}')
        sound = SoundBuffer(length=1)

        sound.write(filename.format('wav'))
        self.assertTrue(path.isfile(filename.format('wav')))

        sound.write(filename.format('flac'))
        self.assertTrue(path.isfile(filename.format('flac')))

        sound.write(filename.format('ogg'))
        self.assertTrue(path.isfile(filename.format('ogg')))

    def test_split_into_blocks(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav').cut(0, 0.11)
        blocksize = 2048
        blocks = list(sound.blocks(blocksize))
        
        # All blocks except the last should be full blocksize
        for i, block in enumerate(blocks[:-1]):
            self.assertEqual(len(block), blocksize)
        
        # Last block should be between 1 and blocksize
        if len(blocks) > 0:
            last_block = blocks[-1]
            self.assertGreater(len(last_block), 0)
            self.assertLessEqual(len(last_block), blocksize)

    def test_split_buffer(self):
        def _split(length):
            sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')

            total = 0
            last_grain = None
            grains_found = 0
            for grain in sound.grains(length):
                total += len(grain)
                last_grain = grain
                grains_found += 1

            # For invalid lengths (<=0), no grains should be generated
            if length <= 0:
                self.assertEqual(grains_found, 0)
                return

            # Check that we got at least one grain and the last grain is not 0
            self.assertGreater(grains_found, 0)
            self.assertIsNotNone(last_grain)
            self.assertNotEqual(len(last_grain), 0)

            # Check that all the grains add up
            self.assertEqual(total, len(sound))

        lengths = [-1, 0, 0.01, 0.121212, 0.3, 0.5599, 0.75, 0.999, 1, 2]
        for length in lengths:
            _split(length)

    def test_random_split_buffer(self):
        base_sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        
        for _ in range(100):
            sound = base_sound.copy()

            total = 0
            for grain in sound.grains(0.001, sound.dur):
                total += len(grain)

            # Check that the remainder grain is not 0
            self.assertNotEqual(len(grain), 0)

            # Check that all the grains add up
            self.assertEqual(total, len(sound))

    def test_window(self):
        sound = SoundBuffer(filename='tests/sounds/whitenoise1s.wav')
        for window_type in (
                'sine', 'sinc', 'saw', 'tri', 'hamm', 
                'hann', 'hannin', 'hannout', 'bart', 
                'gauss', 'gaussin', 'gaussout', 'black',
                'pluckin', 
                'pluckout',
            ):
            s = sound.copy().env(window_type)
            s.graph(f'tests/renders/soundbuffer-windowed-{window_type}.png')

            if window_type in ('hamm', 'black', 'sinc', 'gauss', 'gaussin', 'gaussout'):
                continue

            if not window_type.endswith('out'):
                self.assertEqual(s[0], (0,0))
            else:
                self.assertEqual(s[-1], (0,0))

    def test_wavetable_fill(self):
        for wt_type in ('sine', 'cos', 'square', 'tri', 'tri2', 'saw', 'rsaw', 'rnd'):
            sound = SoundBuffer(length=0.5)
            sound.fill(wt_type)
            sound.graph(f'tests/renders/soundbuffer-wt-fill-{wt_type}.png')

    def test_speed(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        speed = random.random()
        out = sound.speed(speed)
        out.write('tests/renders/soundbuffer_speed.wav')
        self.assertEqual(len(out), int(len(sound) * (1/speed)))

    def test_vpeed(self):
        sound = SoundBuffer(filename='tests/sounds/linux.wav')
        speed = dsp.win('hann', 0.5, 2)
        out = sound.vspeed(speed)
        out.write('tests/renders/soundbuffer_vspeed_0.5_2.wav')

        speed = dsp.win('hann', 0.15, 0.5)
        out = sound.vspeed(speed)
        out.write('tests/renders/soundbuffer_vspeed_0.15_0.5.wav')

        speed = dsp.win('hann', 5, 50)
        out = sound.vspeed(speed)
        out.write('tests/renders/soundbuffer_vspeed_5_50.wav')


    def test_transpose(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')

        speed = random.triangular(1, 10)
        out = sound.transpose(speed)
        self.assertEqual(len(out), len(sound))

        speed = random.triangular(0, 1)
        out = sound.transpose(speed)
        self.assertEqual(len(out), len(sound))

        speed = random.triangular(10, 100)
        out = sound.transpose(speed)
        self.assertEqual(len(out), len(sound))


    def test_pan(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        
        # Test hard panning for linear and constant methods (they hard pan to zero)
        for pan_method in ('linear', 'constant'):
            # Hard pan smoke test
            pan_left = sound.pan(0, method=pan_method)
            # When panning left, right channel (index 1) should be 0
            self.assertEqual(pan_left[random.randint(0, len(pan_left)-1)][1], 0)

            pan_right = sound.pan(1, method=pan_method)
            # When panning right, left channel (index 0) should be 0
            self.assertEqual(pan_right[random.randint(0, len(pan_right)-1)][0], 0)
        
        # Test gogins method (doesn't hard pan to zero, maintains some signal in both channels)
        pan_left_gogins = sound.pan(0, method='gogins')
        pan_right_gogins = sound.pan(1, method='gogins')
        self.assertEqual(len(pan_left_gogins), len(sound))
        self.assertEqual(len(pan_right_gogins), len(sound))
        
        # Verify gogins doesn't zero out channels completely
        left_sample = pan_left_gogins[random.randint(0, len(pan_left_gogins)-1)]
        right_sample = pan_right_gogins[random.randint(0, len(pan_right_gogins)-1)]
        self.assertNotEqual(left_sample[1], 0)  # Right channel should not be zero when panned left
        self.assertNotEqual(right_sample[0], 0)  # Left channel should not be zero when panned right

    def test_slice_frame(self):
        """ A SoundBuffer should return a single frame 
            when sliced into one-dimensionally like:

                frame = sound[frame_index]

            A frame is a tuple of floats, one value 
            for each channel of sound.
        """
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')

        indices = (0, -1, len(sound) // 2, -(len(sound) // 2))

        for frame_index in indices:
            frame = sound[frame_index]
            self.assertTrue(isinstance(frame, tuple))
            self.assertEqual(len(frame), sound.channels)
            self.assertTrue(isinstance(frame[0], float))

    def test_slice_sample(self):
        """ Slicing into the second dimension of a SoundBuffer
            will return a single sample at the given channel index.

                sample = sound[frame_index][channel_index]

            Note: A sample is a float, usually between -1.0 and 1.0 
            but pippi will only clip overflow when you ask it to, or 
            when writing a SoundBuffer back to a file. 
            So, numbers can exceed that range during processing and 
            be normalized or clipped as desired later on.
        """

        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')

        indices = (0, -1, len(sound) // 2, -(len(sound) // 2))

        for frame_index in indices:
            for channel_index in range(sound.channels):
                sample = sound[frame_index][channel_index]
                self.assertTrue(isinstance(sample, float))

    def test_pad_sound_with_silence(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')

        # Pad start
        original_length = len(sound)
        silence_length = random.triangular(0.001, 1)
        sound = sound.pad(silence_length)

        self.assertEqual(len(sound), int((sound.samplerate * silence_length) + original_length))
        self.assertEqual(sound[0], (0,0))

        # Pad end
        original_length = len(sound)
        silence_length = random.triangular(0.001, 1)
        sound = sound.pad(after=silence_length)

        self.assertEqual(len(sound), int((sound.samplerate * silence_length) + original_length))
        self.assertEqual(sound[-1], (0,0))

    def test_trim_silence(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav').env('hannout')
        firstval = abs(sum(sound[0]))
        lastval = abs(sum(sound[-1]))
        sound = sound.pad(before=1, after=1)

        self.assertEqual(sound.dur, 3)

        sound.write('tests/renders/trim_silence_before.wav')

        for threshold in (0, 0.01, 0.5):
            trimstart = sound.trim(start=True, end=False, threshold=threshold)
            trimstart.write('tests/renders/trim_silence_start%s.wav' % threshold)

            trimend = sound.trim(start=False, end=True, threshold=threshold)
            trimend.write('tests/renders/trim_silence_end%s.wav' % threshold)

    def test_taper(self):
        sound = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        sound = sound.taper(0)
        sound = sound.taper(0.001)
        sound = sound.taper(0.01)
        sound = sound.taper(0.1)
        sound = sound.taper(1)
        sound = sound.taper(10)

        self.assertEqual(len(sound), TEST_SAMPLERATE)
        self.assertTrue(sound.samplerate == TEST_SAMPLERATE)

    def test_mul_soundbuffers(self):
        snd = dsp.buffer([1,2,3])
        self.assertEqual(len(snd), 3)
        self.assertEqual(snd * 2, dsp.buffer([2,4,6]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        self.assertEqual(snd * dsp.buffer([1,3,5]), dsp.buffer([1,6,15]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        self.assertEqual(dsp.buffer([1,3,5]) * snd, dsp.buffer([1,6,15]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        snd *= 2
        self.assertEqual(snd, dsp.buffer([2,4,6]))

        snd = dsp.buffer([1,2,3])
        mul = dsp.buffer([2,2,2])
        snd *= mul
        self.assertEqual(snd, dsp.buffer([2,4,6]))

    def test_add_soundbuffers(self):
        snd = dsp.buffer([1,2,3])
        self.assertEqual(len(snd), 3)
        self.assertEqual(snd + 2, dsp.buffer([3,4,5]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        self.assertEqual(snd + dsp.buffer([1,3,5]), dsp.buffer([1,2,3,1,3,5]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        self.assertEqual(dsp.buffer([1,3,5]) + snd, dsp.buffer([1,3,5,1,2,3]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        snd += 2
        self.assertEqual(snd, dsp.buffer([3,4,5]))

    def test_sub_soundbuffers(self):
        snd = dsp.buffer([1,2,3])
        self.assertEqual(len(snd), 3)

        self.assertEqual(snd - 1.5, dsp.buffer([-0.5, 0.5, 1.5]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        self.assertEqual(snd - 2, dsp.buffer([-1,0,1]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        self.assertEqual(snd - dsp.buffer([1,3,5]), dsp.buffer([0,-1,-2]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        self.assertEqual(dsp.buffer([1,3,5]) - snd, dsp.buffer([0,1,2]))
        self.assertEqual(snd, dsp.buffer([1,2,3]))

        snd -= 2
        self.assertEqual(snd, dsp.buffer([-1,0,1]))

    def test_dub_empty_buffer_expansion(self):
        # Test dubbing into an empty buffer should expand it
        empty_buf = SoundBuffer()
        source = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        
        # Dub into empty buffer - should expand automatically
        empty_buf.dub(source)
        
        self.assertEqual(len(empty_buf), len(source))
        self.assertEqual(empty_buf.channels, source.channels)

    def test_dub_beyond_buffer_length(self):
        # Test dubbing beyond the buffer length should expand it
        short_buf = SoundBuffer(length=0.05)  # 0.05 second buffer
        source = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        
        # Dub at position that would exceed the buffer
        start_pos = 0.04  # Start near end of short buffer
        short_buf.dub(source, start_pos)
        
        # Buffer should have expanded to accommodate the full source
        # Use the destination buffer's samplerate for framepos calculation (like dub method does)
        framepos = int(start_pos * short_buf.samplerate)
        expected_length = framepos + len(source)
        self.assertEqual(len(short_buf), expected_length)

    def test_dub_into_zero_length_buffer(self):
        # Test dubbing into a buffer with zero length
        zero_buf = SoundBuffer(length=0)
        source = SoundBuffer(filename='tests/sounds/guitar1s.wav')
        
        zero_buf.dub(source, 0.02)  # Dub at 0.02 seconds
        
        # Buffer should expand to hold the source at the specified position
        # For zero-length buffer, framepos uses the original buffer's samplerate
        original_samplerate = source.samplerate  # used when source SR is <= 0
        framepos = int(0.02 * original_samplerate)
        expected_length = framepos + len(source)
        self.assertEqual(len(zero_buf), expected_length)


