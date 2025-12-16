#!/usr/bin/env python
from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import numpy as np
import os
import subprocess
import sys

# Debug mode can be enabled with DEBUG environment variable
# By default, build in production mode for wheel distribution
dev = 'DEBUG' in os.environ

INCLUDES = ['libpippi/vendor', 'libpippi/src', '/usr/local/include', np.get_include()]
MACROS = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
DIRECTIVES = {}
LIBPIPPI_STATIC = 'libpippi/libpippi.a'
SOUNDPIPE_STATIC = 'libpippi/vendor/soundpipe/libsoundpipe.a'


class BuildExtWithLibpippi(build_ext):
    """Build libpippi.a and libsoundpipe.a first as static libraries for all cython extensions to use"""

    def run(self):
        # Build libpippi.a
        if not os.path.exists(LIBPIPPI_STATIC):
            print(f"Building {LIBPIPPI_STATIC}...")
            self._build_library('libpippi', 'lib')
            print(f"Successfully built {LIBPIPPI_STATIC}")
        else:
            print(f"{LIBPIPPI_STATIC} already exists, skipping build")

        # Build libsoundpipe.a
        if not os.path.exists(SOUNDPIPE_STATIC):
            print(f"Building {SOUNDPIPE_STATIC}...")
            self._build_library('libpippi/vendor/soundpipe', '')
            print(f"Successfully built {SOUNDPIPE_STATIC}")
        else:
            print(f"{SOUNDPIPE_STATIC} already exists, skipping build")

        super().run()

    def _build_library(self, directory, target):
        """Helper to build a library using make"""
        try:
            import multiprocessing
            nproc = multiprocessing.cpu_count()
        except:
            nproc = 1

        # Special handling for Soundpipe - build only what we need
        if 'soundpipe' in directory:
            self._build_soundpipe_minimal(directory)
            return

        # Build command: make [target] -jN
        cmd = ['make']
        if target:
            cmd.append(target)
        cmd.append(f'-j{nproc}')

        result = subprocess.run(
            cmd,
            cwd=directory,
            check=False,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error building in {directory}:", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

    def _build_soundpipe_minimal(self, sp_dir):
        """Build only the Soundpipe modules we actually use"""
        import glob

        # Modules we actually use in pippi.fx (includes transitive dependencies)
        needed_modules = [
            'bal', 'bar', 'base', 'bitcrush', 'butbp', 'butbr', 'buthp', 'butlp',
            'compressor', 'dcblock', 'fft', 'fold', 'ftbl', 'mincer', 'param',
            'paulstretch', 'randmt', 'saturator',
        ]

        # Compiler flags - compatible with GCC 14+
        cflags = [
            '-O3', '-fPIC', '-g',
            '-DUSE_DOUBLE',
            '-DSPFLOAT=double',
            '-DNO_LIBSNDFILE',
            '-Wno-error=incompatible-pointer-types',  # Allow GCC 14+ to build
            f'-I{sp_dir}/h',
            f'-I{sp_dir}/lib/inih',
            f'-I{sp_dir}/lib/faust',
            f'-I{sp_dir}/lib/kissfft',
            '-Dkiss_fft_scalar=double',
            f'-I{sp_dir}/lib/spa',
            f'-I{sp_dir}/lib/openlpc',
            f'-I{sp_dir}/lib/dr_wav',
        ]

        cc = os.environ.get('CC', 'gcc')

        # Create output directories
        os.makedirs(f'{sp_dir}/h', exist_ok=True)
        os.makedirs(f'{sp_dir}/modules', exist_ok=True)
        os.makedirs(f'{sp_dir}/lib/kissfft', exist_ok=True)
        os.makedirs(f'{sp_dir}/lib/fft', exist_ok=True)
        os.makedirs(f'{sp_dir}/lib/inih', exist_ok=True)

        # Build library dependencies (kissfft for mincer/paulstretch, faust for compressor)
        lib_sources = [
            f'{sp_dir}/lib/kissfft/kiss_fft.c',
            f'{sp_dir}/lib/kissfft/kiss_fftr.c',
            f'{sp_dir}/lib/fft/fft.c',  # Will be generated
            f'{sp_dir}/lib/inih/ini.c',
        ]

        # Generate fft.c (concatenate fftlib.c and sp_fft.c)
        fft_c_path = f'{sp_dir}/lib/fft/fft.c'
        if not os.path.exists(fft_c_path):
            with open(fft_c_path, 'w') as fft_out:
                fft_out.write('/* THIS IS A GENERATED FILE. DO NOT EDIT BY HAND */\n')
                with open(f'{sp_dir}/lib/fft/fftlib.c') as f:
                    fft_out.write(f.read())
                with open(f'{sp_dir}/lib/fft/sp_fft.c') as f:
                    fft_out.write(f.read())

        # Generate soundpipe.h header
        sp_h_path = f'{sp_dir}/h/soundpipe.h'
        if not os.path.exists(sp_h_path):
            with open(sp_h_path, 'w') as sp_h:
                sp_h.write('#ifndef SOUNDPIPE_H\n')
                sp_h.write('#define USE_DOUBLE\n')
                sp_h.write('#define SOUNDPIPE_H\n')
                # Include base header and module headers
                for module in needed_modules:
                    h_file = f'{sp_dir}/h/{module}.h'
                    if os.path.exists(h_file):
                        with open(h_file) as hf:
                            sp_h.write(hf.read())
                # Include spa header
                spa_h = f'{sp_dir}/lib/spa/spa.h'
                if os.path.exists(spa_h):
                    with open(spa_h) as hf:
                        sp_h.write(hf.read())
                sp_h.write('#endif\n')

        # Compile library objects
        lib_objs = []
        for src in lib_sources:
            if os.path.exists(src):
                obj = src.replace('.c', '.o')
                cmd = [cc] + cflags + ['-c', src, '-o', obj]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error compiling {src}:", file=sys.stderr)
                    print(result.stderr, file=sys.stderr)
                    sys.exit(1)
                lib_objs.append(obj)

        # Compile module objects
        module_objs = []
        for module in needed_modules:
            src = f'{sp_dir}/modules/{module}.c'
            obj = f'{sp_dir}/modules/{module}.o'
            if os.path.exists(src):
                cmd = [cc] + cflags + ['-c', src, '-o', obj]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error compiling {module}:", file=sys.stderr)
                    print(result.stderr, file=sys.stderr)
                    sys.exit(1)
                module_objs.append(obj)

        # Create static library
        lib_path = f'{sp_dir}/libsoundpipe.a'
        cmd = ['ar', 'rcs', lib_path] + lib_objs + module_objs
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error creating {lib_path}:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

if dev:
    MACROS += [("CYTHON_TRACE_NOGIL", "1"), ("DEBUG", "1")]
    DIRECTIVES['profile'] = True
    DIRECTIVES['linetrace'] = True
    DIRECTIVES['binding'] = True

ext_modules = cythonize([
        Extension('astrid', [
                'astrid.pyx',
                'libpippi/vendor/linenoise/linenoise.c',
                'libpippi/vendor/libpqueue/src/pqueue.c',
                'libpippi/vendor/lmdb/libraries/liblmdb/mdb.c',
                'libpippi/vendor/lmdb/libraries/liblmdb/midl.c',
                'libpippi/vendor/ringbuf/src/ringbuf.c',
                'astrid/src/astrid.c',
            ],
            libraries=['jack', 'rt', 'asound'],
            include_dirs=INCLUDES+[
                'libpippi/vendor/libpqueue/src',
                'libpippi/vendor/linenoise',
                'libpippi/vendor/lmdb/libraries/liblmdb',
                'libpippi/vendor/ringbuf/src',
                'astrid/src'
            ],           
            define_macros=MACROS,
            extra_compile_args=['-g'],
            extra_link_args=['-g'],

            extra_objects=[LIBPIPPI_STATIC],
        ),

        Extension('pippi.events', ['pippi/events.pyx'], include_dirs=INCLUDES, define_macros=MACROS),

        Extension('pippi.defaults', ['pippi/defaults.pyx']), 
        Extension('pippi.dsp', ['pippi/dsp.pyx'], 
            include_dirs=INCLUDES + ['libpippi/vendor/fft'],
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 
        Extension('pippi.fx', [
                'pippi/fx.pyx'
            ],
            include_dirs=INCLUDES + ['libpippi/vendor/fft', 'libpippi/vendor/soundpipe/h'],
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC, SOUNDPIPE_STATIC],
        ),
        Extension('pippi.microsound', [
                'pippi/microsound.pyx'
            ],
            include_dirs=INCLUDES,
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ),
        Extension('pippi.lists', ['pippi/lists.pyx'],
            include_dirs=INCLUDES, 
            define_macros=MACROS
        ),
        Extension('pippi.fft', [
                'pippi/fft.pyx'
            ], 
            include_dirs=INCLUDES + ['libpippi/vendor'],
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 

        Extension('pippi.graph', ['pippi/graph.pyx'], 
            include_dirs=INCLUDES, 
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 

        Extension('pippi.noise', [
                'pippi/noise/noise.pyx'
            ], 
            include_dirs=INCLUDES,
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 
        Extension('pippi.shapes', ['pippi/shapes.pyx'], 
            include_dirs=INCLUDES, 
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 
        Extension('pippi.mir', [
                'pippi/mir.pyx'
            ],
            include_dirs=INCLUDES, 
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ),

        Extension('pippi.oscs', ['pippi/oscs.pyx'], 
            include_dirs=INCLUDES,
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 

        Extension('pippi.midi', ['pippi/midi.pyx'], 
            include_dirs=INCLUDES,
            define_macros=MACROS
        ), 

        Extension('pippi.rand', [
                'pippi/rand.pyx',
            ], 
            include_dirs=INCLUDES, 
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 

        Extension('pippi.soundbuffer', [
                'pippi/soundbuffer.pyx'
            ],
            include_dirs=INCLUDES + ['libpippi/vendor/fft', 'libpippi/vendor/soundpipe/h'],
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 
        Extension('pippi.soundfont', ['pippi/soundfont.pyx'], 
            include_dirs= INCLUDES + ['modules/TinySoundFont'], 
            define_macros=MACROS
        ), 
        Extension('pippi.wavesets', ['pippi/wavesets.pyx'], 
            include_dirs=INCLUDES, 
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 

        # Tuning / scales / harmony / melody
        Extension('pippi.scales', ['pippi/tune/scales.pyx'], 
            include_dirs=INCLUDES,
            define_macros=MACROS
        ), 
        Extension('pippi.intervals', ['pippi/tune/intervals.pyx'], 
            include_dirs=INCLUDES,
            define_macros=MACROS
        ), 
        Extension('pippi.frequtils', ['pippi/tune/frequtils.pyx'], 
            include_dirs=INCLUDES,
            define_macros=MACROS
        ), 
        Extension('pippi.chords', ['pippi/tune/chords.pyx'], 
            include_dirs=INCLUDES,
            define_macros=MACROS
        ), 
        Extension('pippi.tune', ['pippi/tune/tune.pyx'], 
            include_dirs=INCLUDES,
            define_macros=MACROS
        ), 
        Extension('pippi.ugens', [
                'pippi/ugens.pyx'
            ],
            include_dirs=INCLUDES, 
            define_macros=MACROS,
            extra_objects=[LIBPIPPI_STATIC],
        ), 
    ], 
    annotate=dev, 
    compiler_directives=DIRECTIVES,
    gdb_debug=dev,
) 

setup(
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExtWithLibpippi}
)
