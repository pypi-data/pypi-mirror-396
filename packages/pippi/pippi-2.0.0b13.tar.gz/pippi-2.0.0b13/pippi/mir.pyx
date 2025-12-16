#cython: language_level=3
from sys import exit

from pippi.soundbuffer cimport SoundBuffer

import numpy as np
cimport numpy as np


cdef int DEFAULT_WINSIZE = 4096

np.import_array()

cpdef np.ndarray flatten(SoundBuffer snd):
    return np.asarray(snd.remix(1).frames, dtype='d').flatten()

cdef np.ndarray _bandwidth(np.ndarray snd, int samplerate, int winsize):
    import librosa
    return librosa.feature.spectral_bandwidth(y=snd, sr=samplerate, n_fft=winsize)

cpdef SoundBuffer bandwidth(SoundBuffer snd, int winsize=DEFAULT_WINSIZE):
    cdef np.ndarray wt = _bandwidth(flatten(snd), snd.samplerate, winsize)
    return SoundBuffer(wt.transpose().astype('d').flatten(), channels=1, samplerate=snd.samplerate)

cdef np.ndarray _flatness(np.ndarray snd, int winsize):
    import librosa
    return librosa.feature.spectral_flatness(y=snd, n_fft=winsize)

cpdef SoundBuffer flatness(SoundBuffer snd, int winsize=DEFAULT_WINSIZE):
    cdef np.ndarray wt = _flatness(flatten(snd), winsize)
    return SoundBuffer(wt.transpose().astype('d').flatten(), channels=1, samplerate=snd.samplerate)

cdef np.ndarray _rolloff(np.ndarray snd, int samplerate, int winsize):
    import librosa
    return librosa.feature.spectral_rolloff(y=snd, sr=samplerate, n_fft=winsize)

cpdef SoundBuffer rolloff(SoundBuffer snd, int winsize=DEFAULT_WINSIZE):
    cdef np.ndarray wt = _rolloff(flatten(snd), snd.samplerate, winsize)
    return SoundBuffer(wt.transpose().astype('d').flatten(), channels=1, samplerate=snd.samplerate)

cdef np.ndarray _centroid(np.ndarray snd, int samplerate, int winsize):
    import librosa
    return librosa.feature.spectral_centroid(y=snd, sr=samplerate, n_fft=winsize)

cpdef SoundBuffer centroid(SoundBuffer snd, int winsize=DEFAULT_WINSIZE):
    cdef np.ndarray wt = _centroid(flatten(snd), snd.samplerate, winsize)
    return SoundBuffer(wt.transpose().astype('d').flatten(), channels=1, samplerate=snd.samplerate)

cdef np.ndarray _contrast(np.ndarray snd, int samplerate, int winsize):
    import librosa
    return librosa.feature.spectral_contrast(y=snd, sr=samplerate, n_fft=winsize)

cpdef SoundBuffer contrast(SoundBuffer snd, int winsize=DEFAULT_WINSIZE):
    cdef np.ndarray wt = _contrast(flatten(snd), snd.samplerate, winsize)
    return SoundBuffer(wt.transpose().astype('d').flatten(), channels=1, samplerate=snd.samplerate)

cpdef SoundBuffer pitch(SoundBuffer snd, double tolerance=0.8, str method=None, int winsize=DEFAULT_WINSIZE, bint backfill=True, double autotune=0, double fallback=220.):
    """ Returns a wavetable of non-zero frequencies detected which exceed the confidence threshold given. Frequencies are 
        held until the next detection to avoid zeros and outliers. Depending on the input, you may need to play with the 
        tolerance value and the window size to tune the behavior. The default detection method is `yinfast`. 

        Example:

            pitches = mir.pitch(snd, 0.8)

        * Yin implementation ported from:
        * Patrice Guyot. (2018, April 19). Fast Python 
        * implementation of the Yin algorithm (Version v1.1.1). 
        * Zenodo. http://doi.org/10.5281/zenodo.1220947
        * https://github.com/patriceguyot/Yin

        See libpippi/src/mir.c for implementation notes.
    """

    yin = LPPitchTracker.yin_create(4096, <int>snd.samplerate)
    yin.fallback = <lpfloat_t>fallback

    cdef list pitches = []
    cdef double[:] src = flatten(snd)

    cdef lpfloat_t s
    cdef lpfloat_t last_p = -1
    cdef lpfloat_t p = fallback

    for s in src:
        p = LPPitchTracker.yin_process(yin, s);
        if(p > 0 and p != last_p):
            last_p = p
            pitches += [ p ]

    if len(pitches) == 0:
        return None

    return SoundBuffer(pitches, channels=1, samplerate=snd.samplerate)

cpdef list onsets(SoundBuffer snd, str method=None, int winsize=DEFAULT_WINSIZE, bint seconds=True):
    """ Returns a list of onset times in seconds detected using a port of the Coyote onset routine 
        developed by Batuhan Bozkurt originally for the SuperCollider BatUGens.

        An optional `seconds` argument (normally true) may be set to false to return a list of frame indexes instead 
        of seconds.

        Example:
            onsets = mir.onsets(snd)
    """

    cdef lpcoyote_t * od = LPOnsetDetector.coyote_create(snd.samplerate)
    cdef int gate = 1
    cdef int i = 0
    cdef list onsets = []
    cdef double[:] src = flatten(snd)

    for i in range(len(snd)):
        LPOnsetDetector.coyote_process(od, src[i])
        if gate != od.gate:
            if gate == 1 and od.gate == 0:
                onsets += [ i ]
            gate = od.gate

    if seconds:
        onsets = [ onset / <double>snd.samplerate for onset in onsets ]

    return onsets

cpdef list segments(SoundBuffer snd, str method=None, int winsize=DEFAULT_WINSIZE):
    """ A wrapper for `mir.onsets` which returns a list of SoundBuffers sliced at the onset times. 
        See the documentation for `mir.onsets` for an overview of the detection methods available.
    """
    cdef list onset_times = onsets(snd, method, winsize, seconds=False)
    cdef int last = -1
    cdef int onset = 0
    cdef list segments = []

    for onset in onset_times:
        if last < 0:
            last = onset
            continue

        segments += [ snd[last:onset] ]
        last = onset

    if last < len(snd):
        segments += [ snd[last:] ]

    return segments
