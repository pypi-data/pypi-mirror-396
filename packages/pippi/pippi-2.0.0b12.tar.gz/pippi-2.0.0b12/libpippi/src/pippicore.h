#ifndef LP_CORE_H
#define LP_CORE_H

/* std includes */
#include <assert.h>
#include <errno.h>
#include <locale.h>
#include <limits.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <unistd.h>

/* linux platform includes */
#ifdef __linux__
#include <sys/random.h>
#endif

/* Core pippi types and constants */
#include "pippiconstants.h"
#include "pippitypes.h"


/* Users may create custom memorypools. 
 * If the primary memorypool is active, 
 * it will be used to allocate the pool.
 *
 * Otherwise initializtion of the pool 
 * will use the stdlib to calloc the space.
 */
typedef struct lpmemorypool_t {
    unsigned char * pool;
    size_t poolsize;
    size_t pos;
} lpmemorypool_t;

/* Factories & static interfaces */
typedef struct lprand_t {
    lpfloat_t logistic_seed;
    lpfloat_t logistic_x;

    lpfloat_t lorenz_timestep;
    lpfloat_t lorenz_x;
    lpfloat_t lorenz_y;
    lpfloat_t lorenz_z;
    lpfloat_t lorenz_a;
    lpfloat_t lorenz_b;
    lpfloat_t lorenz_c;

    void (*preseed)(void);
    void (*seed)(int);

    lpfloat_t (*stdlib)(lpfloat_t, lpfloat_t);
    lpfloat_t (*logistic)(lpfloat_t, lpfloat_t);

    lpfloat_t (*lorenz)(lpfloat_t, lpfloat_t);
    lpfloat_t (*lorenzX)(lpfloat_t, lpfloat_t);
    lpfloat_t (*lorenzY)(lpfloat_t, lpfloat_t);
    lpfloat_t (*lorenzZ)(lpfloat_t, lpfloat_t);

    lpfloat_t (*rand_base)(lpfloat_t, lpfloat_t);
    lpfloat_t (*rand)(lpfloat_t, lpfloat_t);
    int (*randint)(int, int);
    int (*randbool)(void);
    int (*choice)(int);
} lprand_t;

typedef struct lparray_factory_t {
    lparray_t * (*create)(size_t);
    lparray_t * (*create_from)(int, ...);
    void (*destroy)(lparray_t *);
} lparray_factory_t;

typedef struct lpbuffer_factory_t {
    lpbuffer_t * (*create)(size_t, int, int);
    lpbuffer_t * (*create_from_float)(lpfloat_t value, size_t length, int channels, int samplerate);
    lpbuffer_t * (*create_from_bytes)(char * bytes, size_t length, int channels, int samplerate);
    void (*copy)(lpbuffer_t *, lpbuffer_t *);
    lpbuffer_t * (*clone)(lpbuffer_t *);
    void (*clear)(lpbuffer_t *);
    void (*split2)(lpbuffer_t *, lpbuffer_t *, lpbuffer_t *);
    void (*scale)(lpbuffer_t *, lpfloat_t, lpfloat_t, lpfloat_t, lpfloat_t);
    lpfloat_t (*min)(lpbuffer_t * buf);
    lpfloat_t (*max)(lpbuffer_t * buf);
    lpfloat_t (*mag)(lpbuffer_t * buf);
    lpfloat_t (*avg)(lpbuffer_t * buf);
    lpfloat_t (*play)(lpbuffer_t *, lpfloat_t);
    void (*pan)(lpbuffer_t * buf, lpbuffer_t * pos, int method);
    lpbuffer_t * (*mix)(lpbuffer_t *, lpbuffer_t *);
    lpbuffer_t * (*remix)(lpbuffer_t *, int);
    void (*remap)(lpbuffer_t * dest, lpbuffer_t * src, int map_channels, int * channel_map);
    void (*clip)(lpbuffer_t * buf, lpfloat_t minval, lpfloat_t maxval);
    lpbuffer_t * (*cut)(lpbuffer_t * buf, size_t start, size_t length);
    void (*cut_into)(lpbuffer_t * buf, lpbuffer_t * out, size_t start, size_t length);
    lpbuffer_t * (*varispeed)(lpbuffer_t * buf, lpbuffer_t * speed);
    lpbuffer_t * (*resample)(lpbuffer_t *, size_t);
    void (*multiply)(lpbuffer_t *, lpbuffer_t *);
    void (*multiply_scalar)(lpbuffer_t *, lpfloat_t);
    void (*add)(lpbuffer_t *, lpbuffer_t *);
    void (*add_scalar)(lpbuffer_t *, lpfloat_t);
    void (*subtract)(lpbuffer_t *, lpbuffer_t *);
    void (*subtract_scalar)(lpbuffer_t *, lpfloat_t);
    void (*divide)(lpbuffer_t *, lpbuffer_t *);
    void (*divide_scalar)(lpbuffer_t *, lpfloat_t);
    void (*diff)(lpbuffer_t *, lpbuffer_t *);
    lpbuffer_t * (*concat)(lpbuffer_t *, lpbuffer_t *);
    int (*buffers_are_equal)(lpbuffer_t *, lpbuffer_t *);
    int (*buffers_are_close)(lpbuffer_t *, lpbuffer_t *, int);
    void (*dub)(lpbuffer_t *, lpbuffer_t *, size_t);
    void (*dub_into)(lpbuffer_t * buf, lpbuffer_t * src, size_t offset, lpfloat_t feedback, int wrap, int overdub);
    void (*dub_scalar)(lpbuffer_t *, lpfloat_t, size_t);
    lpfloat_t (*env_process)(lpbuffer_t * env, lpfloat_t freq); /* FIXME maybe this should be under LPEnv or LPLFO or something */
    void (*env)(lpbuffer_t *, lpbuffer_t *);
    lpbuffer_t * (*pad)(lpbuffer_t * buf, size_t before, size_t after);
    void (*taper)(lpbuffer_t * buf, size_t start, size_t end);
    lpbuffer_t * (*trim)(lpbuffer_t * buf, size_t start, size_t end, lpfloat_t threshold, int window);
    lpbuffer_t * (*fadein)(lpbuffer_t * buf, lpfloat_t amount);
    lpbuffer_t * (*fadeout)(lpbuffer_t * buf, lpfloat_t amount);
    void (*fill)(lpbuffer_t * buf, lpbuffer_t * src, int nperiods);
    lpbuffer_t * (*loop)(lpbuffer_t * src, size_t length);
    lpbuffer_t * (*repeat)(lpbuffer_t * src, size_t repeats);
    lpbuffer_t * (*reverse)(lpbuffer_t * buf);
    lpbuffer_t * (*skew)(lpbuffer_t * buf, lpfloat_t tip);
    lpbuffer_t * (*resize)(lpbuffer_t *, size_t);
    void (*plot)(lpbuffer_t * buf);
    void (*destroy)(lpbuffer_t *);
} lpbuffer_factory_t;

typedef struct lpringbuffer_factory_t {
    lpbuffer_t * (*create)(size_t, int, int);
    void (*fill)(lpbuffer_t *, lpbuffer_t *, int);
    lpbuffer_t * (*read)(lpbuffer_t *, size_t);
    void (*readinto)(lpbuffer_t *, lpfloat_t *, size_t, int);
    void (*writefrom)(lpbuffer_t *, lpfloat_t *, size_t, int);
    void (*write)(lpbuffer_t *, lpbuffer_t *);
    lpfloat_t (*readone)(lpbuffer_t *, int);
    void (*writeone)(lpbuffer_t *, lpfloat_t);
    void (*dub)(lpbuffer_t *, lpbuffer_t *);
    void (*destroy)(lpbuffer_t *);
} lpringbuffer_factory_t;

typedef struct lpparam_factory_t {
    lpbuffer_t * (*from_float)(lpfloat_t);
    lpbuffer_t * (*from_int)(int);
    lpsmoother_t (*create_smoother)(lpfloat_t samplerate);
    lpfloat_t (*smooth)(lpsmoother_t * s, lpfloat_t value);
    void (*snap_to_value)(lpsmoother_t * s, lpfloat_t value);
    void (*update_samplerate)(lpsmoother_t * s, lpfloat_t samplerate);
} lpparam_factory_t;

typedef struct lpmemorypool_factory_t {
    /* This is the primary memorypool. */
    unsigned char * pool;
    size_t poolsize;
    size_t pos;

    void (*init)(unsigned char *, size_t);
    lpmemorypool_t * (*custom_init)(unsigned char *, size_t);
    void * (*alloc)(size_t, size_t);
    void * (*custom_alloc)(lpmemorypool_t *, size_t, size_t);
    void (*free)(void *);
} lpmemorypool_factory_t;

typedef struct lpinterpolation_factory_t {
    lpfloat_t (*trunc_pos)(lpbuffer_t *, lpfloat_t);
    lpfloat_t (*trunc)(lpbuffer_t *, lpfloat_t);
    lpfloat_t (*linear_pos)(lpbuffer_t *, lpfloat_t);
    lpfloat_t (*linear_pos2)(lpfloat_t *, size_t, lpfloat_t);
    lpfloat_t (*linear)(lpbuffer_t *, lpfloat_t);
    lpfloat_t (*linear_channel)(lpbuffer_t *, lpfloat_t, int);
    lpbli_t * (*bli_create)(int quality, int loop);
    void (*bli_destroy)(lpbli_t * bli);
    lpfloat_t (*bli_pos)(lpbli_t * bli, lpbuffer_t *, lpfloat_t);
    lpfloat_t (*bli)(lpbli_t * bli, lpbuffer_t *, lpfloat_t);
    lpfloat_t (*hermite_pos)(lpbuffer_t *, lpfloat_t);
    lpfloat_t (*hermite)(lpbuffer_t *, lpfloat_t);
} lpinterpolation_factory_t;

typedef struct lpwavetable_factory_t {
    lpbuffer_t * (*create)(int name, size_t length);
    lpbuffer_t * (*create_stack)(int numtables, size_t * onsets, size_t * lengths, ...);
    void (*destroy)(lpbuffer_t*);
} lpwavetable_factory_t;

typedef struct lpwindow_factory_t {
    lpbuffer_t * (*create)(int name, size_t length);
    lpbuffer_t * (*create_stack)(int numtables, size_t * onsets, size_t * lengths, ...);
    void (*destroy)(lpbuffer_t*);
} lpwindow_factory_t;

typedef struct lpfx_factory_t {
    lpfloat_t (*read_skewed_buffer)(lpfloat_t freq, lpbuffer_t * buf, lpfloat_t phase, lpfloat_t skew);
    lpfloat_t (*lpf1)(lpfloat_t x, lpfloat_t * y, lpfloat_t cutoff, lpfloat_t samplerate);
    lpfloat_t (*hpf1)(lpfloat_t x, lpfloat_t * y, lpfloat_t cutoff, lpfloat_t samplerate);
    void (*convolve)(lpbuffer_t * a, lpbuffer_t * b, lpbuffer_t * out);
    void (*norm)(lpbuffer_t * buf, lpfloat_t ceiling);
    lpfloat_t (*crossover)(lpfloat_t val, lpfloat_t amount, lpfloat_t smooth, lpfloat_t fade);
    lpfloat_t (*fold)(lpfloat_t val, lpfloat_t * prev, lpfloat_t samplerate);
    lpfloat_t (*limit)(lpfloat_t val, lpfloat_t * prev, lpfloat_t threshold, lpfloat_t release, lpbuffer_t * del);
    lpfloat_t (*crush)(lpfloat_t val, int bits);
    lpbalance_t * (*create_balancer)(lpfloat_t samplerate);
    lpfloat_t (*balance)(lpbalance_t * bal, lpfloat_t val, lpfloat_t reference);
    void (*destroy_balancer)(lpbalance_t * bal);
    lpbuffer_t * (*crossfade)(lpbuffer_t * a, lpbuffer_t * b, lpbuffer_t * curve);
    lpfloat_t (*multifade)(lpbuffer_t * buf, lpfloat_t pos, lpfloat_t pan, int method);
    void (*diffuse)(lpbuffer_t * out, size_t frame, lpfloat_t sample, lpfloat_t pan, int method);
    void (*diffuse_into)(lpbuffer_t * out, size_t frame, lpfloat_t sample, lpfloat_t pan, int method);
} lpfx_factory_t;

/* State variable filter & HBAP by Liquid City Motors Will.
 * Ported from cython 2025 by He Can Jog */
typedef struct lpsvf_t {
    lpfloat_t Az[4];
    lpfloat_t Bz[2];
    lpfloat_t Cz[3];
    lpfloat_t X[2];

    lpfloat_t M[3];
    lpfloat_t freq;
    lpfloat_t res;
    lpfloat_t gain;
    lpfloat_t shelf;
    int mode;
} lpsvf_t;

typedef lpfloat_t (*lphbap_process)(void * data, lpfloat_t sample);
typedef struct lphbap_t {
    lpfloat_t d1;
    lpfloat_t d2;
    lpfloat_t d3;
    lpfloat_t a0;
    lpfloat_t a1;
    lphbap_process process;
} lphbap_t;

typedef struct lpfilter_factory_t {
    lpbfilter_t * (*create_bhp)(lpfloat_t cutoff, lpfloat_t samplerate);
    lpfloat_t (*process_bhp)(lpbfilter_t * filter, lpfloat_t in);
    lpbfilter_t * (*create_blp)(lpfloat_t cutoff, lpfloat_t samplerate);
    lpfloat_t (*process_blp)(lpbfilter_t * filter, lpfloat_t in);
    lpsvf_t * (*create_svf)(int svf_mode);
    lpfloat_t (*process_svf)(lpsvf_t * svf, lpfloat_t sample);
    void (*destroy_svf)(lpsvf_t * svf);
} lpfilter_factory_t;

/* Interfaces */
extern const lparray_factory_t LPArray;
extern const lpbuffer_factory_t LPBuffer;
extern const lpringbuffer_factory_t LPRingBuffer;

extern const lpwavetable_factory_t LPWavetable;
extern const lpwindow_factory_t LPWindow;
extern const lpfx_factory_t LPFX;
extern const lpfilter_factory_t LPFilter;

extern lprand_t LPRand;
extern const lpparam_factory_t LPParam;
extern lpmemorypool_factory_t LPMemoryPool;
extern const lpinterpolation_factory_t LPInterpolation;

/* Utilities */

/* The zapgremlins() routine was written by James McCartney as part of SuperCollider:
 * https://github.com/supercollider/supercollider/blob/f0d4f47a33b57b1f855fe9ca2d4cb427038974f0/headers/plugin_interface/SC_InlineUnaryOp.h#L35
 *
 * SuperCollider real time audio synthesis system
 * Copyright (c) 2002 James McCartney. All rights reserved.
 * http://www.audiosynth.com
 *
 * He says:
 *      This is a function for preventing pathological math operations in ugens.
 *      It can be used at the end of a block to fix any recirculating filter values.
 */
lpfloat_t lpzapgremlins(lpfloat_t x);

lpfloat_t lpfilternan(lpfloat_t x);

/* These are little value scaling helper routines. */
/* lpwv wraps a given value between min and max through probably wrong basic arithmetic */
lpfloat_t lpwv(lpfloat_t value, lpfloat_t min, lpfloat_t max);
/* lpsv scales a value normally 0-1 to a custom min and max range */
lpfloat_t lpsv(lpfloat_t value, lpfloat_t min, lpfloat_t max);
/* lpsvf does the same but allows a custom from and to range (like from -1 to 1) */
lpfloat_t lpsvf(lpfloat_t value, lpfloat_t min, lpfloat_t max, lpfloat_t from, lpfloat_t to);

lpfloat_t lpfmax(lpfloat_t a, lpfloat_t b);
lpfloat_t lpfmin(lpfloat_t a, lpfloat_t b);
lpfloat_t lpfabs(lpfloat_t value);
lpfloat_t lpfpow(lpfloat_t value, int exp);
lpfloat_t lpmstofreq(lpfloat_t ms);
lpfloat_t lpstofreq(lpfloat_t seconds);
uint32_t lphashstr(char * str);

lpfloat_t lpphaseinc(lpfloat_t freq, lpfloat_t samplerate);

lpbuffer_t * lpbuffer_create_stack(lpbuffer_t * (*table_creator)(int name, size_t length), int numtables, size_t * onsets, size_t * lengths, va_list vl);

void pan_stereo_constant(lpfloat_t pos, lpfloat_t left_in, lpfloat_t right_in, lpfloat_t * left_out, lpfloat_t * right_out);

/* handle for built-in window TODO think about how to extend this in a simple way for other built-in compile time table defs */
extern const lpfloat_t LPHANN_WINDOW[];

#endif
