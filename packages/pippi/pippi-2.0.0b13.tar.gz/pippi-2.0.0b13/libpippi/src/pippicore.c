#include "pippicore.h"

#ifndef DEBUG
#define DEBUG 0
#endif
#if DEBUG
#include <errno.h>
#endif


/* Forward declarations */
void rand_preseed(void);
void rand_seed(int value);
lpfloat_t rand_base_logistic(lpfloat_t low, lpfloat_t high);
lpfloat_t rand_base_stdlib(lpfloat_t low, lpfloat_t high);
lpfloat_t rand_rand(lpfloat_t low, lpfloat_t high);
lpfloat_t rand_base_lorenz(lpfloat_t low, lpfloat_t high);
lpfloat_t rand_base_lorenzX(lpfloat_t low, lpfloat_t high);
lpfloat_t rand_base_lorenzY(lpfloat_t low, lpfloat_t high);
lpfloat_t rand_base_lorenzZ(lpfloat_t low, lpfloat_t high);
int rand_randint(int low, int high);
int rand_randbool(void);
int rand_choice(int numchoices);

lparray_t * create_array_from(int numvalues, ...);
lparray_t * create_array(size_t length);
void destroy_array(lparray_t * array);

lpbuffer_t * create_buffer(size_t length, int channels, int samplerate);
lpbuffer_t * create_buffer_from_float(lpfloat_t value, size_t length, int channels, int samplerate);
lpbuffer_t * create_buffer_from_bytes(char * bytes, size_t length, int channels, int samplerate);
lpbuffer_t * clone_buffer(lpbuffer_t * src);
void copy_buffer(lpbuffer_t * src, lpbuffer_t * dest);
void clear_buffer(lpbuffer_t * buf);
void scale_buffer(lpbuffer_t * buf, lpfloat_t from_min, lpfloat_t from_max, lpfloat_t to_min, lpfloat_t to_max);
lpfloat_t min_buffer(lpbuffer_t * buf);
lpfloat_t max_buffer(lpbuffer_t * buf);
lpfloat_t mag_buffer(lpbuffer_t * buf);
lpfloat_t avg_buffer(lpbuffer_t * buf);
void multiply_buffer(lpbuffer_t * a, lpbuffer_t * b);
void scalar_multiply_buffer(lpbuffer_t * a, lpfloat_t b);
void add_buffers(lpbuffer_t * a, lpbuffer_t * b);
void scalar_add_buffer(lpbuffer_t * a, lpfloat_t b);
void subtract_buffers(lpbuffer_t * a, lpbuffer_t * b);
void scalar_subtract_buffer(lpbuffer_t * a, lpfloat_t b);
void divide_buffers(lpbuffer_t * a, lpbuffer_t * b);
void scalar_divide_buffer(lpbuffer_t * a, lpfloat_t b);
void difference_buffers(lpbuffer_t * a, lpbuffer_t * b);
lpbuffer_t * concat_buffers(lpbuffer_t * a, lpbuffer_t * b);
int buffers_are_equal(lpbuffer_t * a, lpbuffer_t * b);
int buffers_are_close(lpbuffer_t * a, lpbuffer_t * b, int d);
void dub_buffer(lpbuffer_t * a, lpbuffer_t * b, size_t start);
void dub_into_buffer(lpbuffer_t * buf, lpbuffer_t * src, size_t offset, lpfloat_t feedback, int wrap, int overdub);
void dub_scalar(lpbuffer_t * a, lpfloat_t, size_t start);
lpfloat_t env_process(lpbuffer_t * env, lpfloat_t pos);
void env_buffer(lpbuffer_t * buf, lpbuffer_t * env);
lpbuffer_t * pad_buffer(lpbuffer_t * buf, size_t before, size_t after); 
void taper_buffer(lpbuffer_t * buf, size_t start, size_t end);
lpbuffer_t * trim_buffer(lpbuffer_t * buf, size_t start, size_t end, lpfloat_t threshold, int window);
void plot_buffer(lpbuffer_t * buf);
lpfloat_t play_buffer(lpbuffer_t * buf, lpfloat_t speed);
void split2_buffer(lpbuffer_t * src, lpbuffer_t * a, lpbuffer_t * b);
lpbuffer_t * mix_buffers(lpbuffer_t * a, lpbuffer_t * b);
lpbuffer_t * remix_buffer(lpbuffer_t * buf, int channels);
void remap_buffer(lpbuffer_t * dest, lpbuffer_t * src, int map_channels, int * channel_map);
void clip_buffer(lpbuffer_t * buf, lpfloat_t minval, lpfloat_t maxval);
lpbuffer_t * cut_buffer(lpbuffer_t * buf, size_t start, size_t length);
void cut_into_buffer(lpbuffer_t * buf, lpbuffer_t * out, size_t start, size_t length);
lpbuffer_t * varispeed_buffer(lpbuffer_t * buf, lpbuffer_t * speed);
lpbuffer_t * resample_buffer(lpbuffer_t * buf, size_t length);
void pan_stereo_buffer(lpbuffer_t * buf, lpbuffer_t * pos, int method);
void fill_buffer(lpbuffer_t * buf, lpbuffer_t * src, int nperiods);
lpbuffer_t * loop_into_buffer(lpbuffer_t * buf, size_t length);
lpbuffer_t * repeat_buffer(lpbuffer_t * buf, size_t repeats);
lpbuffer_t * reverse_buffer(lpbuffer_t * buf);
lpbuffer_t * skew_buffer(lpbuffer_t * buf, lpfloat_t tip);
lpbuffer_t * resize_buffer(lpbuffer_t *, size_t);
lpbuffer_t * fadein_buffer(lpbuffer_t * buf, lpfloat_t amount);
lpbuffer_t * fadeout_buffer(lpbuffer_t * buf, lpfloat_t amount);
void destroy_buffer(lpbuffer_t * buf);

lpfloat_t read_skewed_buffer(lpfloat_t freq, lpbuffer_t * buf, lpfloat_t phase, lpfloat_t skew);
lpfloat_t fx_lpf1(lpfloat_t x, lpfloat_t * y, lpfloat_t cutoff, lpfloat_t samplerate);
lpfloat_t fx_hpf1(lpfloat_t x, lpfloat_t * y, lpfloat_t cutoff, lpfloat_t samplerate);
void fx_convolve(lpbuffer_t * a, lpbuffer_t * b, lpbuffer_t * out);
void fx_norm(lpbuffer_t * buf, lpfloat_t ceiling);
lpfloat_t fx_fold(lpfloat_t val, lpfloat_t * prev, lpfloat_t samplerate);
lpfloat_t fx_crossover(lpfloat_t val, lpfloat_t amount, lpfloat_t smooth, lpfloat_t fade);
lpfloat_t fx_limit(lpfloat_t val, lpfloat_t * prev, lpfloat_t threshold, lpfloat_t release, lpbuffer_t * del);
lpfloat_t fx_crush(lpfloat_t val, int bits);
lpbfilter_t * fx_butthp_create(lpfloat_t cutoff, lpfloat_t samplerate);
lpfloat_t fx_butthp(lpbfilter_t * filter, lpfloat_t in);
lpbfilter_t * fx_buttlp_create(lpfloat_t cutoff, lpfloat_t samplerate);
lpfloat_t fx_buttlp(lpbfilter_t * filter, lpfloat_t in);
lpbalance_t * fx_create_balancer(lpfloat_t samplerate);
lpfloat_t fx_balance(lpbalance_t * bal, lpfloat_t val, lpfloat_t reference);
void fx_destroy_balancer(lpbalance_t * bal);
lpbuffer_t * fx_crossfade(lpbuffer_t * a, lpbuffer_t * b, lpbuffer_t * curve);
lpfloat_t fx_multifade(lpbuffer_t * buf, lpfloat_t pos, lpfloat_t pan, int method);
void fx_diffuse(lpbuffer_t * out, size_t frame, lpfloat_t sample, lpfloat_t pan, int method);
void fx_diffuse_into(lpbuffer_t * out, size_t frame, lpfloat_t sample, lpfloat_t pan, int method);
lpsvf_t * fx_svf_create(int mode);
lpfloat_t fx_svf_process(lpsvf_t * svf, lpfloat_t sample);
void fx_svf_destroy(lpsvf_t * svf);

lpbuffer_t * ringbuffer_create(size_t length, int channels, int samplerate);
void ringbuffer_fill(lpbuffer_t * ringbuf, lpbuffer_t * buf, int offset);
lpfloat_t ringbuffer_readone(lpbuffer_t * ringbuf, int offset);
lpbuffer_t * ringbuffer_read(lpbuffer_t * ringbuf, size_t length);
void ringbuffer_readinto(lpbuffer_t * ringbuf, lpfloat_t * data, size_t length, int channels);
void ringbuffer_writeone(lpbuffer_t * ringbuf, lpfloat_t sample);
void ringbuffer_writefrom(lpbuffer_t * ringbuf, lpfloat_t * data, size_t length, int channels);
void ringbuffer_write(lpbuffer_t * ringbuf, lpbuffer_t * buf);
void ringbuffer_dub(lpbuffer_t * buf, lpbuffer_t * src);
void ringbuffer_destroy(lpbuffer_t * buf);

void memorypool_init(unsigned char * pool, size_t poolsize);
lpmemorypool_t * memorypool_custom_init(unsigned char * pool, size_t poolsize);
void * memorypool_alloc(size_t itemcount, size_t itemsize);
void * memorypool_custom_alloc(lpmemorypool_t * pool, size_t itemcount, size_t itemsize);
void memorypool_free(void * ptr);

lpfloat_t interpolate_hermite(lpbuffer_t * buf, lpfloat_t phase);
lpfloat_t interpolate_hermite_pos(lpbuffer_t * buf, lpfloat_t pos);
lpfloat_t interpolate_linear(lpbuffer_t * buf, lpfloat_t phase);
lpfloat_t interpolate_linear_pos(lpbuffer_t * buf, lpfloat_t pos);
lpfloat_t interpolate_linear_pos2(lpfloat_t * buf, size_t length, lpfloat_t pos);
lpfloat_t interpolate_linear_channel(lpbuffer_t* buf, lpfloat_t phase, int channel);
lpfloat_t interpolate_trunc(lpbuffer_t * buf, lpfloat_t phase);
lpfloat_t interpolate_trunc_pos(lpbuffer_t * buf, lpfloat_t pos);
lpbli_t * interpolate_bli_create(int quality, int loop);
void interpolate_bli_destroy(lpbli_t * bli);
lpfloat_t interpolate_bli_get_filter_coeff(lpbli_t * bli, lpfloat_t pos);
lpfloat_t interpolate_bli(lpbli_t * bli, lpbuffer_t * buf, lpfloat_t phase);
lpfloat_t interpolate_bli_pos(lpbli_t * bli, lpbuffer_t * buf, lpfloat_t pos);
lpfloat_t interpolate_bli_get_filter_coeff(lpbli_t * bli, lpfloat_t filter_phasor);

lpbuffer_t * param_create_from_float(lpfloat_t value);
lpbuffer_t * param_create_from_int(int value);
lpsmoother_t param_smoother_create(lpfloat_t samplerate);
void param_smoother_snap_to_value(lpsmoother_t * smoother, lpfloat_t value);
void param_smoother_update_samplerate(lpsmoother_t * smoother, lpfloat_t samplerate);
lpfloat_t param_smooth(lpsmoother_t * s, lpfloat_t value);

lpbuffer_t * create_wavetable(int name, size_t length);
void destroy_wavetable(lpbuffer_t* buf);
lpbuffer_t* create_window(int name, size_t length);
lpbuffer_t * lpbuffer_create_stack(lpbuffer_t * (*table_creator)(int name, size_t length), int numtables, size_t * onsets, size_t * lengths, va_list vl);
lpbuffer_t * create_window_stack(int numtables, size_t * onsets, size_t * lengths, ...);
lpbuffer_t * create_wavetable_stack(int numtables, size_t * onsets, size_t * lengths, ...);
void destroy_window(lpbuffer_t* buf);

/* Populate interfaces */
lprand_t LPRand = { LOGISTIC_SEED_DEFAULT, LOGISTIC_X_DEFAULT, \
    LORENZ_TIMESTEP_DEFAULT, \
    LORENZ_X_DEFAULT, LORENZ_Y_DEFAULT, LORENZ_Z_DEFAULT, \
    LORENZ_A_DEFAULT, LORENZ_B_DEFAULT, LORENZ_C_DEFAULT, \
    rand_preseed, rand_seed, rand_base_stdlib, rand_base_logistic, \
    rand_base_lorenz, rand_base_lorenzX, rand_base_lorenzY, rand_base_lorenzZ, \
    rand_base_stdlib, rand_rand, rand_randint, rand_randbool, rand_choice };
lpmemorypool_factory_t LPMemoryPool = { 0, 0, 0, memorypool_init, memorypool_custom_init, memorypool_alloc, memorypool_custom_alloc, memorypool_free };
const lparray_factory_t LPArray = { create_array, create_array_from, destroy_array };
const lpbuffer_factory_t LPBuffer = { 
    create_buffer, 
    create_buffer_from_float, 
    create_buffer_from_bytes, 
    copy_buffer, 
    clone_buffer, 
    clear_buffer, 
    split2_buffer, 
    scale_buffer, 
    min_buffer, 
    max_buffer, 
    mag_buffer, 
    avg_buffer, 
    play_buffer, 
    pan_stereo_buffer, 
    mix_buffers, 
    remix_buffer, 
    remap_buffer, 
    clip_buffer, 
    cut_buffer, 
    cut_into_buffer, 
    varispeed_buffer, 
    resample_buffer, 
    multiply_buffer, 
    scalar_multiply_buffer, 
    add_buffers, 
    scalar_add_buffer, 
    subtract_buffers, 
    scalar_subtract_buffer, 
    divide_buffers, 
    scalar_divide_buffer, 
    difference_buffers, 
    concat_buffers, 
    buffers_are_equal, 
    buffers_are_close, 
    dub_buffer, 
    dub_into_buffer, 
    dub_scalar, 
    env_process, 
    env_buffer, 
    pad_buffer, 
    taper_buffer, 
    trim_buffer, 
    fadein_buffer, 
    fadeout_buffer, 
    fill_buffer, 
    loop_into_buffer, 
    repeat_buffer, 
    reverse_buffer, 
    skew_buffer,
    resize_buffer, 
    plot_buffer, 
    destroy_buffer 
};
const lpinterpolation_factory_t LPInterpolation = { 
    interpolate_trunc_pos, 
    interpolate_trunc, 
    interpolate_linear_pos, 
    interpolate_linear_pos2, 
    interpolate_linear, 
    interpolate_linear_channel, 
    interpolate_bli_create,
    interpolate_bli_destroy,
    interpolate_bli_pos, 
    interpolate_bli, 
    interpolate_hermite_pos, 
    interpolate_hermite 
};
const lpparam_factory_t LPParam = { param_create_from_float, param_create_from_int, param_smoother_create, param_smooth, param_smoother_snap_to_value, param_smoother_update_samplerate };
const lpwavetable_factory_t LPWavetable = { create_wavetable, create_wavetable_stack, destroy_wavetable };
const lpwindow_factory_t LPWindow = { create_window, create_window_stack, destroy_window };
const lpringbuffer_factory_t LPRingBuffer = { ringbuffer_create, ringbuffer_fill, ringbuffer_read, ringbuffer_readinto, ringbuffer_writefrom, ringbuffer_write, ringbuffer_readone, ringbuffer_writeone, ringbuffer_dub, ringbuffer_destroy };
const lpfx_factory_t LPFX = {
    read_skewed_buffer,
    fx_lpf1,
    fx_hpf1,
    fx_convolve,
    fx_norm,
    fx_crossover,
    fx_fold,
    fx_limit,
    fx_crush,
    fx_create_balancer,
    fx_balance,
    fx_destroy_balancer,
    fx_crossfade,
    fx_multifade,
    fx_diffuse,
    fx_diffuse_into
};
const lpfilter_factory_t LPFilter = { 
    fx_butthp_create, 
    fx_butthp, 
    fx_buttlp_create, 
    fx_buttlp,
    fx_svf_create,
    fx_svf_process,
    fx_svf_destroy
};

/* Platform-specific random seed, called 
 * on program init (and on process pool init) 
 * from python or optionally elsewhere to 
 * seed random with nice bytes. */
void rand_preseed() {
#ifdef __linux__
    unsigned int * buffer;
    ssize_t bytes_read;
    size_t buffer_size;
    buffer_size = sizeof(unsigned int);
    buffer = LPMemoryPool.alloc(1, buffer_size);
    bytes_read = getrandom(buffer, buffer_size, 0);
    if(bytes_read > 0) srand(*buffer);
    free(buffer);
#endif
}

/* User rand seed */
void rand_seed(int value) {
    srand((unsigned int)value);
}

/* Default rand_base callback. 
 *
 * These base rand_base callbacks return 0-1 and 
 * are the basis of all other rand functions like 
 * choice and randint.
 *
 * They may be swapped out at runtime by setting 
 * LPRand.rand_base to the desired rand_base pointer;
 * */
lpfloat_t rand_base_stdlib(lpfloat_t low, lpfloat_t high) {
    return (rand()/(lpfloat_t)RAND_MAX) * (high-low) + low;
}

/* Logistic rand base. */
lpfloat_t rand_base_logistic(lpfloat_t low, lpfloat_t high) {
    LPRand.logistic_x = LPRand.logistic_seed * LPRand.logistic_x * (1.f - LPRand.logistic_x);
    return LPRand.logistic_x * (high-low) + low;
}

/* The three Lorenz attractor implementations (lorenzX, lorenzY, lorenzZ) 
 * were lightly adapted with permission from Greg Cope's helpful overview: 
 *      https://www.algosome.com/articles/lorenz-attractor-programming-code.html
 * Please consider those routines to be included here under an MIT license.
 */
lpfloat_t lorenzX(lpfloat_t low, lpfloat_t high) {
    LPRand.lorenz_x = LPRand.lorenz_x + LPRand.lorenz_timestep * LPRand.lorenz_a * (LPRand.lorenz_y - LPRand.lorenz_x);
    return LPRand.lorenz_x * (high-low) + low;
}

lpfloat_t lorenzY(lpfloat_t low, lpfloat_t high) {
    LPRand.lorenz_y = LPRand.lorenz_y + LPRand.lorenz_timestep * (LPRand.lorenz_x * (LPRand.lorenz_b - LPRand.lorenz_z) - LPRand.lorenz_y);
    return LPRand.lorenz_y * (high-low) + low;
}

lpfloat_t lorenzZ(lpfloat_t low, lpfloat_t high) {
    LPRand.lorenz_z = LPRand.lorenz_z + LPRand.lorenz_timestep * (LPRand.lorenz_x * LPRand.lorenz_y - LPRand.lorenz_c * LPRand.lorenz_z);
    return LPRand.lorenz_z * (high-low) + low;
}

lpfloat_t rand_base_lorenzX(lpfloat_t low, lpfloat_t high) {
    lpfloat_t x;
    x = lorenzX(low, high);
    lorenzY(low, high);
    lorenzZ(low, high);
    return x;
}

lpfloat_t rand_base_lorenzY(lpfloat_t low, lpfloat_t high) {
    lpfloat_t y;
    lorenzX(low, high);
    y = lorenzY(low, high);
    lorenzZ(low, high);
    return y;
}

lpfloat_t rand_base_lorenzZ(lpfloat_t low, lpfloat_t high) {
    lpfloat_t z;
    lorenzX(low, high);
    lorenzY(low, high);
    z = lorenzZ(low, high);
    return z;
}

lpfloat_t rand_base_lorenz(lpfloat_t low, lpfloat_t high) {
    lpfloat_t x, y, z, val;
    x = lorenzX(0, 1);
    y = lorenzY(0, 1);
    z = lorenzZ(0, 1);
    val = x * y * z;
    while(val > high) {
        val -= (high-low);
    }
    while(val < low) {
        val += (high-low);
    }

    return val;
}

lpfloat_t rand_rand(lpfloat_t low, lpfloat_t high) {
    return LPRand.rand_base(low, high);
}

int rand_randint(int low, int high) {
    float diff, tmp;

    tmp = (float)rand_rand((lpfloat_t)low, (lpfloat_t)high);
    diff = (int)tmp - tmp;

    if(diff >= 0.5f) {
        return (int)ceil(tmp);
    } else {
        return (int)floor(tmp);
    }
}

int rand_randbool(void) {
    return rand_randint(0, 1);
}

int rand_choice(int numchoices) {
#if DEBUG
    assert(numchoices > 0);
#endif
    if(numchoices == 1) return 0;
    return rand_randint(0, numchoices);
}

lparray_t * create_array(size_t length) {
    size_t i = 0;
    lparray_t * array = (lparray_t*)LPMemoryPool.alloc(1, sizeof(lparray_t));
    array->data = (int*)LPMemoryPool.alloc(length, sizeof(int));
    array->length = length;
    for(i=0; i < array->length; i++) {
        array->data[i] = 0;
    }
    array->phase = 0.f;
    return array;
}

lparray_t * create_array_from(int numvalues, ...) {
    va_list vl;
    lparray_t * array;
    int i;

    va_start(vl, numvalues);

    array = (lparray_t*)LPMemoryPool.alloc(1, sizeof(lparray_t));
    array->data = (int*)LPMemoryPool.alloc(numvalues, sizeof(int));

    for(i=0; i < numvalues; i++) {
        array->data[i] = va_arg(vl, int);
    }

    va_end(vl);

    return array;
}

void destroy_array(lparray_t * array) {
    if(array != NULL) {
        LPMemoryPool.free(array->data);
        LPMemoryPool.free(array);
    }
}

/* Buffer
 * */
lpbuffer_t * create_buffer(size_t length, int channels, int samplerate) {
    lpbuffer_t * buf;
    size_t bufsize = sizeof(lpbuffer_t) + (length * channels * sizeof(lpfloat_t));

    buf = (lpbuffer_t*)LPMemoryPool.alloc(1, bufsize);
    if(buf == NULL) {
        fprintf(stderr, "Could not alloc memory for buffer struct\n");
        return NULL;
    }

    memset(buf, 0, bufsize);
    buf->channels = channels;
    buf->length = length;
    buf->samplerate = samplerate;
    buf->boundary = length-1;
    buf->range = length;
    return buf;
}

lpbuffer_t * create_buffer_from_float(lpfloat_t value, size_t length, int channels, int samplerate) {
    size_t i;
    int c;
    lpbuffer_t * buf;
    buf = create_buffer(length, channels, samplerate);
    for(i=0; i < length; i++) {
        for(c=0; c < channels; c++) {
            buf->data[i * channels + c] = value;
        }
    }
    return buf;
}

lpbuffer_t * create_buffer_from_bytes(char * bytes, size_t length, int channels, int samplerate) {
    size_t i;
    char val = 0;
    lpbuffer_t * buf;
    buf = create_buffer(length, channels, samplerate);
    for(i=0; i < buf->length * channels; i++) {
        val = (int)bytes[i];
        buf->data[i] = (float)(val / CHAR_MAX);
    }

    return buf;
}

/*
void stack2_buffer(lpbuffer_t * src, lpbuffer_t * a, lpbuffer_t * b) {
    size_t i;

    assert(src->channels == 2);

    a = LPBuffer.create(src->length, 1, src->samplerate);
    b = LPBuffer.create(src->length, 1, src->samplerate);

    for(i=0; i < src->length; i++) {
        a->data[i] = src->data[i * 2];        
        a->data[i * 2] = src->data[i * 2 + 1];        
    }
}
*/


void split2_buffer(lpbuffer_t * src, lpbuffer_t * a, lpbuffer_t * b) {
    size_t i;

#if DEBUG
    assert(src->channels == 2);
    assert(src->length == a->length);
    assert(src->length == b->length);
#endif

    for(i=0; i < src->length; i++) {
        a->data[i] = src->data[i * 2];        
        b->data[i] = src->data[i * 2 + 1];        
    }
}

void copy_buffer(lpbuffer_t * src, lpbuffer_t * dest) {
    size_t i;
    int c;

#if DEBUG
    assert(src->length == dest->length);
    assert(src->channels == dest->channels);
#endif

    for(i=0; i < src->length; i++) {
        for(c=0; c < src->channels; c++) {
            dest->data[i * src->channels + c] = src->data[i * src->channels + c];
        }
    }
}

lpbuffer_t * clone_buffer(lpbuffer_t * src) {
    lpbuffer_t * out = create_buffer(src->length, src->channels, src->samplerate);
    memcpy(out->data, src->data, src->length * src->channels * sizeof(lpfloat_t));
    return out;
}

void clear_buffer(lpbuffer_t * buf) {
    memset(buf->data, 0, buf->length * buf->channels * sizeof(lpfloat_t));
}

void scale_buffer(lpbuffer_t * buf, lpfloat_t from_min, lpfloat_t from_max, lpfloat_t to_min, lpfloat_t to_max) {
    size_t i;
    int c, idx;
    lpfloat_t from_diff, to_diff;

    to_diff = to_max - to_min;;
    from_diff = from_max - from_min;;

    /* Maybe this is valid? It's weird to "scale" 
     * a buffer filled with one value, but I guess 
     * that's a case we should support...
     * Ideally we'll figure out how to get rid of that 
     * repeating divide and use an approach that supports 
     * this case.
     * Anyway: TODO handle this better?
     */
#if DEBUG
    assert(from_diff != 0);
#endif

    for(i=0; i < buf->length; i++) {
        for(c=0; c < buf->channels; c++) {
            idx = i * buf->channels + c;
            buf->data[idx] = ((buf->data[idx] - from_min) / from_diff) * to_diff + to_min;
        }
    }
}

lpfloat_t min_buffer(lpbuffer_t * buf) {
    lpfloat_t out = 0.f;
    size_t i;
    int c;

    for(i=0; i < buf->length; i++) {
        for(c=0; c < buf->channels; c++) {
            if(i==0 && c==0) {
                out = buf->data[i * buf->channels + c];
                continue;
            }
            out = fmin(buf->data[i * buf->channels + c], out);
        }
    }
    return out;
}

lpfloat_t max_buffer(lpbuffer_t * buf) {
    lpfloat_t out = 0.f;
    size_t i;
    int c;

    for(i=0; i < buf->length; i++) {
        for(c=0; c < buf->channels; c++) {
            if(i==0 && c==0) {
                out = buf->data[i * buf->channels + c];
                continue;
            }
            out = fmax(buf->data[i * buf->channels + c], out);
        }
    }
    return out;
}

lpfloat_t mag_buffer(lpbuffer_t * buf) {
    lpfloat_t out = 0.f;
    size_t i;
    int c;

    for(i=0; i < buf->length; i++) {
        for(c=0; c < buf->channels; c++) {
            out = fmax(fabs(buf->data[i * buf->channels + c]), out);
        }
    }
    return out;
}

lpfloat_t avg_buffer(lpbuffer_t * buf) {
    lpfloat_t sum = 0.f;
    size_t i;
    int c;

    if(buf->length <= 0 || buf->channels <= 0) return 0.f;

    for(i=0; i < buf->length; i++) {
        for(c=0; c < buf->channels; c++) {
            sum += buf->data[i * buf->channels + c];
        }
    }
    return sum / (lpfloat_t)(buf->length * buf->channels);
}

void pan_stereo_constant(lpfloat_t pos, lpfloat_t left_in, lpfloat_t right_in, lpfloat_t * left_out, lpfloat_t * right_out) {
    *left_out = left_in * (lpfloat_t)sqrt(1.f - pos);
    *right_out = right_in * (lpfloat_t)sqrt(pos);
}

void pan_stereo_linear(lpfloat_t pos, lpfloat_t left_in, lpfloat_t right_in, lpfloat_t * left_out, lpfloat_t * right_out) {
    *left_out = left_in * (1.f - pos);
    *right_out = right_in * pos;
}

void pan_stereo_sine(lpfloat_t pos, lpfloat_t left_in, lpfloat_t right_in, lpfloat_t * left_out, lpfloat_t * right_out) {
    *left_out = left_in * (lpfloat_t)sin(pos * (lpfloat_t)HALFPI);
    *right_out = right_in * (lpfloat_t)cos(pos * (lpfloat_t)HALFPI);
}

void pan_stereo_gogins(lpfloat_t pos, lpfloat_t left_in, lpfloat_t right_in, lpfloat_t * left_out, lpfloat_t * right_out) {
    *left_out = left_in * (lpfloat_t)sin((pos + 0.5f) * (lpfloat_t)HALFPI);
    *right_out = right_in * (lpfloat_t)cos((pos + 0.5f) * (lpfloat_t)HALFPI);
}

void pan_stereo_buffer(lpbuffer_t * buf, lpbuffer_t * pos, int method) {
    void (*handler)(lpfloat_t, lpfloat_t, lpfloat_t, lpfloat_t *, lpfloat_t *);
    lpfloat_t _pos;
    size_t i;

#if DEBUG
    assert(buf->channels == 2);
#endif

    if(method == PANMETHOD_CONSTANT) {
        handler = &pan_stereo_constant;
    } else if(method == PANMETHOD_LINEAR) {
        handler = &pan_stereo_linear;
    } else if(method == PANMETHOD_SINE) {
        handler = &pan_stereo_sine;
    } else if(method == PANMETHOD_GOGINS) {
        handler = &pan_stereo_gogins;
    } else {
        handler = &pan_stereo_constant;
    }

    for(i=0; i < buf->length; i++) {
        _pos = interpolate_linear_pos(pos, (lpfloat_t)i/buf->length);
        handler(_pos, buf->data[i*2], buf->data[i*2+1], &buf->data[i*2], &buf->data[i*2+1]);
    }
}

lpfloat_t play_buffer(lpbuffer_t * buf, lpfloat_t speed) {
    lpfloat_t phase_inc, value;
    phase_inc = 1.f / (buf->length * (1.f / speed));
    value = interpolate_linear_pos(buf, buf->phase);
    buf->phase += phase_inc;
    return value;
}

lpbuffer_t * varispeed_buffer(lpbuffer_t * buf, lpbuffer_t * speed) {
    lpbuffer_t * out;
    lpbuffer_t * trimmed;
    lpfloat_t pos, phase_inc, phase, _speed, minspeed;
    size_t i, length;
    int c;

    minspeed = fmax(LPVSPEED_MIN, min_buffer(speed));
    length = (size_t)(buf->length * (1.f/minspeed));

    phase = 0.f;
    phase_inc = (1.f/buf->length) * (buf->length-1);

#if DEBUG
    assert(length > 1);
#endif

    out = create_buffer(length, buf->channels, buf->samplerate);
    for(i=0; i < length; i++) {
        pos = (lpfloat_t)i / length;

        for(c=0; c < buf->channels; c++) {
            out->data[i * buf->channels + c] = interpolate_linear_channel(buf, phase, c);
        }

        _speed = interpolate_linear_pos(speed, pos);
        phase += phase_inc * _speed;
        if(phase >= buf->length) break;
    }

    trimmed = cut_buffer(out, 0, i);
    free(out);
    return trimmed;
}

lpbuffer_t * resample_buffer(lpbuffer_t * buf, size_t length) {
    lpbuffer_t * out;
    lpfloat_t pos;
    lpfloat_t sample;
    size_t i;
    int c;

#if DEBUG
    assert(length > 1);
#endif
    out = create_buffer(length, buf->channels, buf->samplerate);
    for(i=0; i < length; i++) {
        pos = (lpfloat_t)i/(length-1);
        for(c=0; c < buf->channels; c++) {
            sample = interpolate_linear_channel(buf, pos * buf->length, c);
            out->data[i * buf->channels + c] = sample;
        }
    }

    return out;
}

void multiply_buffer(lpbuffer_t * a, lpbuffer_t * b) {
    size_t length, i;
    int c, j;
    length = (a->length <= b->length) ? a->length : b->length;
    for(i=0; i < length; i++) {
        for(c=0; c < a->channels; c++) {
            j = c % b->channels;
            a->data[i * a->channels + c] *= b->data[i * b->channels + j];
        }
    }
}

void scalar_multiply_buffer(lpbuffer_t * a, lpfloat_t b) {
    size_t i;
    int c;
    for(i=0; i < a->length; i++) {
        for(c=0; c < a->channels; c++) {
            a->data[i * a->channels + c] *= b;
        }
    }
}

lpbuffer_t * concat_buffers(lpbuffer_t * a, lpbuffer_t * b) {
    size_t length, i;
    int c, channels;
    lpbuffer_t * out;

    length = a->length + b->length;
    channels = a->channels;
    out = create_buffer(length, channels, a->samplerate);

    for(i=0; i < a->length; i++) {
        for(c=0; c < channels; c++) {
            out->data[i * channels + c] = a->data[i * channels + c];
        }
    }

    for(i=a->length; i < length; i++) {
        for(c=0; c < channels; c++) {
            out->data[i * channels + c] = b->data[(i-a->length) * channels + c];
        }
    }

    return out;
}

void add_buffers(lpbuffer_t * a, lpbuffer_t * b) {
    size_t length, i;
    int c, j;
    length = (a->length <= b->length) ? a->length : b->length;
    for(i=0; i < length; i++) {
        for(c=0; c < a->channels; c++) {
            j = c % b->channels;
            a->data[i * a->channels + c] += b->data[i * b->channels + j];
        }
    }
}

void scalar_add_buffer(lpbuffer_t * a, lpfloat_t b) {
    size_t i;
    int c;
    for(i=0; i < a->length; i++) {
        for(c=0; c < a->channels; c++) {
            a->data[i * a->channels + c] += b;
        }
    }
}

void subtract_buffers(lpbuffer_t * a, lpbuffer_t * b) {
    size_t length, i;
    int c, j;
    length = (a->length <= b->length) ? a->length : b->length;
    for(i=0; i < length; i++) {
        for(c=0; c < a->channels; c++) {
            j = c % b->channels;
            a->data[i * a->channels + c] -= b->data[i * b->channels + j];
        }
    }
}

void scalar_subtract_buffer(lpbuffer_t * a, lpfloat_t b) {
    size_t i;
    int c;
    for(i=0; i < a->length; i++) {
        for(c=0; c < a->channels; c++) {
            a->data[i * a->channels + c] -= b;
        }
    }
}

void divide_buffers(lpbuffer_t * a, lpbuffer_t * b) {
    size_t length, i;
    int c, j;
    length = (a->length <= b->length) ? a->length : b->length;
    for(i=0; i < length; i++) {
        for(c=0; c < a->channels; c++) {
            j = c % b->channels;
            if(b->data[i * b->channels + j] == 0) {
                a->data[i * a->channels + c] = 0.f;
            } else {
                a->data[i * a->channels + c] /= b->data[i * b->channels + j];
            }
        }
    }
}

void scalar_divide_buffer(lpbuffer_t * a, lpfloat_t b) {
    size_t i;
    int c;
    if(b == 0) {
        for(i=0; i < a->length; i++) {
            for(c=0; c < a->channels; c++) {
                a->data[i * a->channels + c] = 0.f;
            }
        }
    } else {
        for(i=0; i < a->length; i++) {
            for(c=0; c < a->channels; c++) {
                a->data[i * a->channels + c] /= b;
            }
        }
    }
}

void difference_buffers(lpbuffer_t * a, lpbuffer_t * b) {
    size_t length, i;
    int c, j;
    length = (a->length <= b->length) ? a->length : b->length;
    for(i=0; i < length; i++) {
        for(c=0; c < a->channels; c++) {
            j = c % b->channels;
            a->data[i * a->channels + c] += (b->data[i * b->channels + j] * (lpfloat_t)(-1.0));
        }
    }
}

int buffers_are_equal(lpbuffer_t * a, lpbuffer_t * b) {
    size_t i;
    int c;
    if(a->length != b->length) return 0;
    if(a->channels != b->channels) return 0;
    for(i=0; i < a->length; i++) {
        for(c=0; c < a->channels; c++) {
            if(a->data[i * a->channels + c] != b->data[i * a->channels + c]) return 0;
        }
    }
    return 1;
}

int buffers_are_close(lpbuffer_t * a, lpbuffer_t * b, int d) {
    size_t i;
    int c;
    long atmp, btmp;
    if(a->length != b->length) return 0;
    if(a->channels != b->channels) return 0;
    for(i=0; i < a->length; i++) {
        for(c=0; c < a->channels; c++) {
            atmp = floor(a->data[i * a->channels + c] * d);
            btmp = floor(b->data[i * a->channels + c] * d);
            if(atmp != btmp) return 0;
        }
    }
    return 1;
}

lpfloat_t env_process(lpbuffer_t * env, lpfloat_t freq) {
    lpfloat_t sample=0.f;
    sample = interpolate_linear_pos(env, env->phase);
    env->phase += (1.f / (lpfloat_t)env->length) * freq;
    while(env->phase >= 1.f) env->phase -= 1.f;
    return sample;
}

void env_buffer(lpbuffer_t * buf, lpbuffer_t * env) {
    lpfloat_t value;
    size_t i;
    int c;

#if DEBUG
    assert(env->length > 0);
    assert(env->channels == 1);
#endif

    for(i=0; i < buf->length; i++) {
        value = interpolate_linear(env, ((lpfloat_t)i/buf->length) * env->length);
        for(c=0; c < buf->channels; c++) {
            buf->data[i * buf->channels + c] *= value;
        }
    }
}

lpbuffer_t * pad_buffer(lpbuffer_t * buf, size_t before, size_t after) {
    size_t length, i;
    int c;
    lpbuffer_t * out;

    length = buf->length + before + after;
    out = LPBuffer.create(length, buf->channels, buf->samplerate);

    for(i=0; i < buf->length; i++) {
        for(c=0; c < out->channels; c++) {
            out->data[(i+before) * out->channels + c] = buf->data[i * out->channels + c];
        }
    }

    return out;
}

lpfloat_t _sum_abs_frame(lpbuffer_t * buf, size_t pos) {
    int c;
    lpfloat_t current;
    current = 0;
    for(c=0; c < buf->channels; c++) {
        current += buf->data[pos * buf->channels + c];
    }

    current /= (lpfloat_t)buf->channels;
    current = fabs(current);

    return current; 
}

void taper_buffer(lpbuffer_t * buf, size_t start, size_t end) {
    lpfloat_t frac, a, b, phase, sample, mul;
    size_t i, offset, winlength;
    int c, hi;

#if DEBUG
    assert(start <= buf->length);
    assert(end <= buf->length);
#endif

    winlength = HANN_WINDOW_SIZE / 2;

    start = (start > buf->length) ? buf->length : start;
    end = (end > buf->length) ? buf->length : end;

    if(start > 0) {
        for(i=0; i < start; i++) {
            phase = ((lpfloat_t)i / start) * (winlength-1);
            frac = phase - (int)phase;
            hi = (int)phase;
            a = LPWIN_HANN[hi];
            b = LPWIN_HANN[hi+1];
            mul = (1.0f - frac) * a + (frac * b);

            for(c=0; c < buf->channels; c++) {
                sample = mul * buf->data[i * buf->channels + c];
                buf->data[i * buf->channels + c] = sample;
            }
        }
    }

    if(end > 0) {
        for(i=0; i < end; i++) {
            offset = buf->length - end;
            phase = ((lpfloat_t)i / end) * (winlength-1);
            frac = phase - (int)phase;
            hi = (int)phase + winlength;
            a = LPWIN_HANN[hi];
            b = LPWIN_HANN[hi+1];
            mul = (1.0f - frac) * a + (frac * b);

            for(c=0; c < buf->channels; c++) {
                sample = mul * buf->data[(offset + i) * buf->channels + c];
                buf->data[(offset + i) * buf->channels + c] = sample;
            }
        }
    }
}

lpbuffer_t * trim_buffer(lpbuffer_t * buf, size_t start, size_t end, lpfloat_t threshold, int window) {
    size_t boundary, trimend, trimstart, length, i;
    lpbuffer_t * out;
    lpfloat_t current;
    int c, hits;

    boundary = buf->length - 1;
    trimend = boundary;
    trimstart = 0;
    current = 0.f;
    hits = 0;

    if(end==1) {
        while(1) {
            current = _sum_abs_frame(buf, trimend);
            if(current > threshold) hits += 1;
            trimend -= 1;
            if(trimend <= 0 || hits >= window) break;
        }
    }

    if(start==1) {
        hits = 0;
        while(1) {
            current = _sum_abs_frame(buf, trimstart);
            if(current > threshold) hits += 1;
            trimstart += 1;
            if(trimstart >= boundary || hits >= window) break;
        }
    }

    length = trimend - trimstart;
    out = LPBuffer.create(length, buf->channels, buf->samplerate);

    for(i=0; i < length; i++) {
        for(c=0; c < buf->channels; c++) {
            out->data[i * buf->channels + c] = buf->data[(trimstart + i) * buf->channels + c];
        }
    }

    return out;
}

void print_pixels(int * pixels, int width, int height) {
    int x, y;
    for(y=0; y < height; y++) {
        for(x=0; x < width; x++) {
            fprintf(stdout, "%d", pixels[x * PIXEL_HEIGHT + y]);
        }
        fprintf(stdout, "\n");
    }
}

wchar_t get_grid_char(int pixels[BRAILLE_WIDTH * BRAILLE_HEIGHT]) {
    int i, r;
    int map[BRAILLE_WIDTH * BRAILLE_HEIGHT] = {0,2,4,1,3,5,6,7};

    /* Braille dots are indexed like this:
     *   1 4
     *   2 5
     *   3 6 
     *   7 8
     *
     * Mapped to pixel inputs:
     *
     *   pixels:   0  1  2  3  4  5  6  7
     *   braille:  0  2  4  1  3  5  6  7
     *   byte idx: 1  2  4  8  16 32 64 128
     */
    //print_pixels(pixels, BRAILLE_WIDTH, BRAILLE_HEIGHT);
    r = 0;
    fprintf(stderr, "BEG\n");
    for(i=0; i < BRAILLE_WIDTH * BRAILLE_HEIGHT; i++) {
        fprintf(stderr, "pixels[map[%d]]=%d pixels[%d]=%d\n", i, pixels[map[i]], i, pixels[i]);
        if(pixels[map[i]] == 1) {
            fprintf(stderr, "  map[%d]: %d exp2(%d): %d\n", i, map[i], i, (int)exp2(i));
            r += (int)exp2(i);
        }
    }
    fprintf(stderr, "END\n");

    return (wchar_t)(GRID_EMPTY + r);
}

void copy_pixels_to_block(int * pixels, int offset_x, int offset_y, int * block, int width, int height) {
    int x, y, px, py;
    for(x=0; x < width; x++) {
        for(y=0; y < height; y++) {
            px = x + offset_x;
            py = y + offset_y;
            block[x * height + y] = pixels[px * PIXEL_HEIGHT + py];
        }
    }
}

void plot_buffer(lpbuffer_t * buf) {
    size_t i, pos, blocksize;
    int c;
    int color;
    int px, py1, py2, py;
    int cx, cy;
    float sample, peak, low;
    wchar_t w;

    int pixel_block[BRAILLE_WIDTH * BRAILLE_HEIGHT] = {0};
    int pixels[PIXEL_WIDTH * PIXEL_HEIGHT] = {0};

    blocksize = (size_t)(buf->length / (float)PIXEL_WIDTH);

    pos = 0;
    px = 0;
    py1 = 0;
    py2 = 0;

    /* Trace a temporary pixel buffer:
     *     1s at peaks and lows, 0s elsewhere.
     *
     * Width is PIXEL_WIDTH 
     *     where each pixel is a 1 at the averaged peaks and 
     *     lows of the block size computed from the buffer length.
     *
     * Height is PIXEL_HEIGHT
     *     with buffer values scaled from 
     *     a -1.f to 1.f domain to 
     *     a range of 0 to PIXEL_HEIGHT pixels.
     */
    while(pos <= buf->length-blocksize) {
        peak = 0;
        low = 0;

        for(i=0; i < blocksize; i++) {
            sample = 0.f;
            for(c=0; c < buf->channels; c++) {
                sample += (float)buf->data[(i+pos) * buf->channels + c];
            }

            peak = fmax(peak, sample);
            low = fmin(low, sample);
        }

        peak = fmin(1.f, (peak+1.f)/2.f);
        low = fmax(0.f, (low+1.f)/2.f);

        py1 = (int)(peak * PIXEL_HEIGHT);
        py2 = (int)(low * PIXEL_HEIGHT);
        pixels[px * PIXEL_HEIGHT + py1] = 1;
        pixels[px * PIXEL_HEIGHT + py2] = 1;

        pos += blocksize;
        px += 1;

#if DEBUG
        assert(px <= PIXEL_WIDTH);
#endif
    }


    print_pixels(pixels, PIXEL_WIDTH, PIXEL_HEIGHT);
    /* for each braille char row */
    for(cy=0; cy < PLOT_HEIGHT; cy++) {
        /* for each braille char column in this row */
        py = cy * BRAILLE_HEIGHT;
        for(cx=0; cx < PLOT_WIDTH; cx++) {
            px = cx * BRAILLE_WIDTH;

            copy_pixels_to_block(pixels, px, py, pixel_block, BRAILLE_WIDTH, BRAILLE_HEIGHT);
            fprintf(stderr, "\n\npixel_block\n");
            //print_pixels(pixel_block, BRAILLE_WIDTH, BRAILLE_HEIGHT);
            color = 255; // FIXME do something fun (or useful?)
            printf("\033[38;5;%dm", color);
            w = get_grid_char(pixel_block);
            printf("%lc", w);
            fprintf(stderr, "GOT %lc\n\n", w);
        } 
        printf("\n");
    }
    printf("\033[0m");
    printf("\n\n");

}

void dub_buffer(lpbuffer_t * a, lpbuffer_t * b, size_t start) {
    size_t i;
    int c, j;
    lpfloat_t sample;

#if DEBUG
    assert(start + b->length <= a->length);
    assert(b->length <= a->length);
    assert(a->channels == b->channels);
#endif

    for(i=0; i < b->length; i++) {
        for(c=0; c < a->channels; c++) {
            j = c % b->channels;
            sample = b->data[i * b->channels + j];
            a->data[(i+start) * a->channels + c] += sample;
        }
    }
}

void dub_into_buffer(
        lpbuffer_t * buf, 
        lpbuffer_t * src, 
        size_t offset, 
        lpfloat_t feedback,
        int wrap,
        int overdub
    ) {
    size_t i, j, dublength, slop=0;
    int c, d;
    lpfloat_t sample;

    dublength = src->length;
    slop = (src->length + offset) - buf->length;
    if(slop > 0) dublength -= slop;

    if(overdub == 0) {
        memset(buf->data+(offset*buf->channels), 0, sizeof(lpfloat_t) * buf->channels * dublength);
    }

    for(i=0; i < dublength; i++) {
        for(c=0; c < buf->channels; c++) {
            d = c % src->channels;
            sample = buf->data[(i+offset) * buf->channels + c] * feedback;
            sample += src->data[i * src->channels + d];
            buf->data[(i+offset) * buf->channels + c] = sample;
        }
    }

    if(wrap == 1 && slop > 0) {
        for(j=0; j < slop; j++) {
            for(c=0; c < buf->channels; c++) {
                d = c % src->channels;
                sample = buf->data[j * buf->channels + c] * feedback;
                sample += src->data[(i+j) * src->channels + d];
                buf->data[j * buf->channels + c] = sample;
            }
        }
    }
}



void dub_scalar(lpbuffer_t * a, lpfloat_t val, size_t start) {
    int c;

#if DEBUG
    assert(start < a->length);
#endif
    for(c=0; c < a->channels; c++) {
        a->data[start * a->channels + c] += val;
    }
}

void cut_into_buffer(lpbuffer_t * buf, lpbuffer_t * out, size_t start, size_t length) {
    size_t i, writelength;
    int c;

    /* FIXME support zero-length buffers */
#if DEBUG
    assert(length > 0);
#endif

    if(start < buf->length) {
        writelength = buf->length - start;
        writelength = (writelength > length) ? length : writelength;
        for(i=0; i < writelength; i++) {
            for(c=0; c < buf->channels; c++) {
                out->data[i * buf->channels + c] = buf->data[(i+start) * buf->channels + c];
            }
        }
    }
}

void clip_buffer(lpbuffer_t * buf, lpfloat_t minval, lpfloat_t maxval) {
    size_t i, elements;
    elements = buf->length * buf->channels;
    for(i=0; i < elements; i++) {
        buf->data[i] = fmin(fmax(buf->data[i], minval), maxval);
    }
}

lpbuffer_t * cut_buffer(lpbuffer_t * buf, size_t start, size_t length) {
    lpbuffer_t * out;

    /* FIXME support zero-length buffers */
#if DEBUG
    assert(length > 0);
#endif

    out = LPBuffer.create(length, buf->channels, buf->samplerate);
    cut_into_buffer(buf, out, start, length);
    return out;
}

lpbuffer_t * mix_buffers(lpbuffer_t * a, lpbuffer_t * b) {
    int max_channels, max_samplerate, c;
    size_t i;
    lpbuffer_t * out;
    lpbuffer_t * longest;
    lpbuffer_t * shortest;

    if(a->length >= b->length) {
        longest=a; shortest=b;
    } else {
        longest=b; shortest=a;
    }

    max_channels = (a->channels >= b->channels) ? a->channels : b->channels;
    max_samplerate = (a->samplerate >= b->samplerate) ? a->samplerate : b->samplerate;
    out = LPBuffer.create(longest->length, max_channels, max_samplerate);

    for(i=0; i < longest->length; i++) {
        for(c=0; c < max_channels; c++) {
            out->data[i * max_channels + c] += longest->data[i * max_channels + c];
        }
    }

    for(i=0; i < shortest->length; i++) {
        for(c=0; c < max_channels; c++) {
            out->data[i * max_channels + c] += shortest->data[i * max_channels + c];
        }
    }

    return out;
}

void remap_buffer(lpbuffer_t * dest, lpbuffer_t * src, int map_channels, int * channel_map) {
    size_t i;
    int c, c_dest;

    for(i=0; i < src->length; i++) {
        if(i >= dest->length) break;
        for(c=0; c < map_channels; c++) {
            if(c >= map_channels || c >= dest->channels || c >= src->channels || channel_map[c] < 0) continue;
            c_dest = channel_map[c];
            dest->data[i * dest->channels + c_dest] = src->data[i * src->channels + c];
        }
    }
}

lpbuffer_t * remix_buffer(lpbuffer_t * buf, int channels) {
    size_t i;
    int c, ci;
    lpbuffer_t * newbuf;
    lpfloat_t sample, phase, frac, a, b;

    newbuf = create_buffer(buf->length, channels, buf->samplerate);

    if(channels <= 1) {
        for(i=0; i < buf->length; i++) {
            for(c=0; c < buf->channels; c++) {
                newbuf->data[i] += buf->data[i * buf->channels + c];
            }
        }
    } else {
        for(i=0; i < buf->length; i++) {
            for(c=0; c < channels; c++) {
                phase = (c / (lpfloat_t)(channels-1)) * buf->channels;
                ci = (int)phase;
                frac = phase - ci;
                a = buf->data[i * buf->channels + (ci % buf->channels)];
                b = buf->data[i * buf->channels + ((ci+1) % buf->channels)];
                sample = (1.0f - frac) * a + (frac * b);
                newbuf->data[i * channels + c] = sample;
            }
        }
    }

    return newbuf;
}

lpbuffer_t * remix_buffer_to_channels(lpbuffer_t * buf, int * channels, int num_channels) {
    size_t i;
    int c;
    lpbuffer_t * newbuf;

#if DEBUG
    assert(num_channels > 0);
#endif

    newbuf = create_buffer(buf->length, num_channels, buf->samplerate);

    for(i=0; i < buf->length; i++) {
        for(c=0; c < num_channels; c++) {
            if((channels[c]-1) >= buf->channels) continue;
            newbuf->data[i * num_channels + c] = buf->data[i * buf->channels + (channels[c]-1)];
        }
    }

    return newbuf;
}

void fill_buffer(lpbuffer_t * buf, lpbuffer_t * src, __attribute((unused)) int nperiods) {
    size_t i;
    int c;
    lpfloat_t pos;

    // FIXME incorporate nperiods to modulate the number of periods for the src buffer

    for(i=0; i < buf->length; i++) {
        pos = (lpfloat_t)i / buf->length;
        for(c=0; c < buf->channels; c++) {
            buf->data[i * buf->channels + c] = interpolate_linear_channel(src, pos * src->length, c % src->channels);
        }
    }
}

lpbuffer_t * loop_into_buffer(lpbuffer_t * buf, size_t length) {
    size_t i, j;
    int c;
    lpbuffer_t * out;
    out = create_buffer(length, buf->channels, buf->samplerate);

    for(i=0; i < length; i++) {
        j = i % buf->length;
        for(c=0; c < out->channels; c++) {
            out->data[i * out->channels + c] = buf->data[j * out->channels + c];
        }
    }

    return out;
}

lpbuffer_t * repeat_buffer(lpbuffer_t * buf, size_t repeats) {
    size_t length, pos, i;
    lpbuffer_t * out;
    length = buf->length * repeats;
    out = create_buffer(length, buf->channels, buf->samplerate);

    pos = 0;
    for(i=0; i < repeats; i++) {
        dub_buffer(out, buf, pos);
        pos += buf->length;
    }

    return out;
}

lpbuffer_t * reverse_buffer(lpbuffer_t * buf) {
    size_t i, r;
    int c;
    lpbuffer_t * out;
    out = create_buffer(buf->length, buf->channels, buf->samplerate);

    for(c=0; c < buf->channels; c++) {
        for(i=0; i < buf->length; i++) {
            r = buf->length - i - 1;
            out->data[r * buf->channels + c] = buf->data[i * buf->channels + c];
        }
    }

    return out;
}

lpbuffer_t * skew_buffer(lpbuffer_t * buf, lpfloat_t tip) {
    size_t i;
    int c;
    lpfloat_t phase=0, warp, m=0.5f-tip,pos=0;
    lpbuffer_t * out = create_buffer(buf->length, buf->channels, buf->samplerate);
    for(c=0; c < out->channels; c++) {
        for(i=0; i < out->length; i++) {
            pos = (lpfloat_t)i / (out->length-1);
            if(pos < tip) {
                warp = m * (pos / tip);
            } else {
                warp = m * ((1.f-pos) / (1.f-tip));
            }
            warp *= buf->length;
            out->data[i * out->channels + c] = LPInterpolation.linear_channel(buf, phase+warp, c);
        }
    }
    return out;
}

lpbuffer_t * resize_buffer(lpbuffer_t * buf, size_t length) {
    size_t i;
    int c;
    lpbuffer_t * newbuf;

    newbuf = create_buffer(length, buf->channels, buf->samplerate);

    for(i=0; i < length; i++) {
        if(i >= buf->length) break;
        for(c=0; c < buf->channels; c++) {
            newbuf->data[i * buf->channels + c] = buf->data[i * buf->channels + c];    
        }
    }

    destroy_buffer(buf);
    return newbuf;
}

lpbuffer_t * fadein_buffer(lpbuffer_t * buf, lpfloat_t amount) {
    size_t i;
    int c;
    lpfloat_t phase, fade_factor;
    lpbuffer_t * out;
    
    out = create_buffer(buf->length, buf->channels, buf->samplerate);
    amount *= -50.0f;
    
    for(i = 0; i < buf->length; i++) {
        phase = (lpfloat_t)i / buf->length;
        fade_factor = 1.0f - expf(amount * phase);
        
        for(c = 0; c < buf->channels; c++) {
            out->data[i * buf->channels + c] = buf->data[i * buf->channels + c] * fade_factor;
        }
    }
    
    return out;
}

lpbuffer_t * fadeout_buffer(lpbuffer_t * buf, lpfloat_t amount) {
    size_t i;
    int c;
    lpfloat_t phase, fade_factor;
    lpbuffer_t * out;
    
    out = create_buffer(buf->length, buf->channels, buf->samplerate);
    amount *= -50.0f;
    
    for(i = 0; i < buf->length; i++) {
        phase = (lpfloat_t)i / buf->length;
        fade_factor = expf(amount * phase);
        
        for(c = 0; c < buf->channels; c++) {
            out->data[i * buf->channels + c] = buf->data[i * buf->channels + c] * fade_factor;
        }
    }
    
    return out;
}

void destroy_buffer(lpbuffer_t * buf) {
    LPMemoryPool.free(buf);
}

/* Basic FX / waveshaping
 */
lpfloat_t read_skewed_buffer(lpfloat_t freq, lpbuffer_t * buf, lpfloat_t phase, lpfloat_t skew) {
    lpfloat_t warp, m, pos;

    m = 0.5f - skew;

    pos = phase / buf->length;
    if(phase < skew) {
        warp = m * (pos / skew);
    } else {
        warp = m * ((1.f-pos) / (1.f-skew));
    }

    return LPInterpolation.linear(buf, (phase + (warp * buf->length)) * freq);
}

lpfloat_t fx_lpf1(lpfloat_t x, lpfloat_t * y, lpfloat_t cutoff, lpfloat_t samplerate) {
    lpfloat_t gamma = 1.f - (lpfloat_t)exp(-(2.f * (lpfloat_t)PI) * (cutoff/samplerate));
    *y = (1.f - gamma) * (*y) + gamma * x;
    return *y;
}

lpfloat_t fx_hpf1(lpfloat_t x, lpfloat_t * y, lpfloat_t cutoff, lpfloat_t samplerate) {
    lpfloat_t gamma = 1.f - (lpfloat_t)exp(-(2.f * (lpfloat_t)PI) * (cutoff/samplerate));
    *y = (1.f - gamma) * (*y) + gamma * x;
    return x - *y;
}

/* State variable filter by Liquid City Motors Will
 * Ported from cython in 2025 by He Can Jog 
 *
 * Will's notes & comments are preserved in the implementation below.
 * ---
 *
 * 2nd order state variable filter cookbook adapted from google ipython notebook
 * https://github.com/google/music-synthesizer-for-android/blob/master/lab/Second%20order%20sections%20in%20matrix%20form.ipynb
 * trapezoidal integration from Andrew Simper http://www.cytomic.com/files/dsp/SvfLinearTrapOptimised2.pdf
 * */
lpsvf_t * fx_svf_create(int mode) {
    lpsvf_t * svf = LPMemoryPool.alloc(1, sizeof(lpsvf_t));
    memset(svf, 0, sizeof(lpsvf_t));
    svf->freq = 100.f;
    svf->res = 0;
    svf->gain = 0;
    svf->mode = mode;
    return svf;
}

void fx_svf_core(lpsvf_t * svf) {
#if LP_FLOAT
    svf->res = lpfmax(lpfmin(svf->res, 1.f), 0.f);
    lpfloat_t g = tanf((lpfloat_t)PI * svf->freq) * (lpfloat_t)svf->shelf;

    lpfloat_t k = 2.f - 2.f * svf->res;

    lpfloat_t a1 = 1.f / (1.f + g * (g + k));
    lpfloat_t a2 = g * a1;
    lpfloat_t a3 = g * a2;

    svf->Az[0] = 2.f * a1 - 1.f;
    svf->Az[1] = -2.f * a2;
    svf->Az[2] = 2.f * a2;
    svf->Az[3] = 1.f - 2.f * a3;

    svf->Bz[0] = 2.f * a2;
    svf->Bz[1] = 2.f * a3;
#else
    svf->res = lpfmax(lpfmin(svf->res, 1.), 0.);
    lpfloat_t g = tan(PI * svf->freq) * svf->shelf;

    lpfloat_t k = 2. - 2. * svf->res;

    lpfloat_t a1 = 1. / (1. + g * (g + k));
    lpfloat_t a2 = g * a1;
    lpfloat_t a3 = g * a2;

    svf->Az[0] = 2. * a1 - 1.;
    svf->Az[1] = -2. * a2;
    svf->Az[2] = 2. * a2;
    svf->Az[3] = 1. - 2. * a3;

    svf->Bz[0] = 2. * a2;
    svf->Bz[1] = 2. * a3;
#endif

    lpfloat_t C_v0[3] = {1, 0, 0};
    lpfloat_t C_v1[3] = {a2, a1, -a2};
    lpfloat_t C_v2[3] = {a3, a2, 1-a3};

    svf->Cz[0] = C_v0[0] * svf->M[0] + C_v1[0] * svf->M[1]  + C_v2[0] * svf->M[2];
    svf->Cz[1] = C_v0[1] * svf->M[0] + C_v1[1] * svf->M[1]  + C_v2[1] * svf->M[2];
    svf->Cz[2] = C_v0[2] * svf->M[0] + C_v1[2] * svf->M[1]  + C_v2[2] * svf->M[2];
}

lpfloat_t fx_svf_process(lpsvf_t * svf, lpfloat_t sample) {
    lpfloat_t out=0, A=0, A2=0, k=0;
    switch(svf->mode) {
        case FILTER_LOWPASS:
            svf->M[0] = 0;
            svf->M[1] = 0;
            svf->M[2] = 1;
            svf->shelf = 1;
            break;
        case FILTER_BANDPASS:
            svf->M[0] = 0;
            svf->M[1] = 1;
            svf->M[2] = 0;
            svf->shelf = 1;
            break;
        case FILTER_HIGHPASS:
            k = 2 - 2 * svf->res;
            svf->M[0] = 1;
            svf->M[1] = -k;
            svf->M[2] = -1;
            svf->shelf = 1;
            break;
        case FILTER_NOTCH:
            k = 2 - 2 * svf->res;
            svf->M[0] = 1;
            svf->M[1] = -k;
            svf->M[2] = 0;
            svf->shelf = 1;
            break;
        case FILTER_PEAK:
            k = 2 - 2 * svf->res;
            svf->M[0] = 1;
            svf->M[1] = -k;
            svf->M[2] = -2;
            svf->shelf = 1;
            break;
        case FILTER_BELL:
#if LP_FLOAT
            A = powf(10, svf->gain / 40.f);
            k = 1.f / (svf->res*A);
            svf->res = 1 - 0.5f * k;
            svf->M[0] = 1;
            svf->M[1] = k * (A - 1);
            svf->M[2] = 0;
            svf->shelf = 1;
#else
            A = pow(10, svf->gain / 40.f);
            k = 1. / (svf->res*A);
            svf->res = 1 - 0.5 * k;
            svf->M[0] = 1;
            svf->M[1] = k * (A - 1);
            svf->M[2] = 0;
            svf->shelf = 1;
#endif
            break;
        case FILTER_LOWSHELF:
#if LP_FLOAT
            A = powf(10, svf->gain / 40.f);
#else
            A = pow(10, svf->gain / 40.);
#endif
            k = 1.f/(svf->res);
            svf->res = 1.f - 0.5f * k;
            svf->M[0] = 1;
            svf->M[1] = k * (A - 1);
            svf->M[2] = A * A - 1;
#if LP_FLOAT
            svf->shelf = 1.f/sqrtf(A);
#else
            svf->shelf = 1.f/sqrt(A);
#endif
            break;
        case FILTER_HIGHSHELF:
#if LP_FLOAT
            A = powf(10, svf->gain / 40.f);
#else
            A = pow(10, svf->gain / 40.);
#endif
            A2 = A * A;
            k = 1.f/(svf->res);
            svf->res = 1.f - 0.5f * k;
            svf->M[0] = A2;
            svf->M[1] = k * (A - A2);
            svf->M[2] = 1 - A2;
#if LP_FLOAT
            svf->shelf = sqrtf(A);
#else
            svf->shelf = sqrt(A);
#endif
            break;
        default:
            break;
    }

    fx_svf_core(svf);

    out = sample * svf->Cz[0] + svf->X[0] * svf->Cz[1] + svf->X[1] * svf->Cz[2];
    svf->X[0] = sample * svf->Bz[0] + svf->X[0] * svf->Az[0] + svf->X[1] * svf->Az[1];
    svf->X[1] = sample * svf->Bz[1] + svf->X[0] * svf->Az[2] + svf->X[1] * svf->Az[3];

    return out;
}

void fx_svf_destroy(lpsvf_t * svf) {
    LPMemoryPool.free(svf);
}

/* These butterworth filters were ported from the filters
 * included with Paul Batchelor's Soundpipe, in turn ported 
 * from csound.
 *
 * The original Soundpipe annotation is preserved below.
 *
 * Original Author(s): Paris Smaragdis, John ffitch
 * Year: 1994
 * Location: Opcodes/butter.c
 */
lpbfilter_t * fx_butthp_create(lpfloat_t cutoff, lpfloat_t samplerate) {
    lpbfilter_t * filter = LPMemoryPool.alloc(1, sizeof(lpbfilter_t));
    memset(filter, 0, sizeof(lpbfilter_t));

    filter->sr = samplerate;
    filter->freq = cutoff;
    filter->pidsr = (lpfloat_t)PI / samplerate;

    return filter;
}

lpfloat_t fx_butthp(lpbfilter_t * filter, lpfloat_t in) {
    lpfloat_t t, y, c, out = 0.f;

    if(filter->freq <= 0.f) return 0.f;

    if(filter->freq != filter->lkf) {
        filter->lkf = filter->freq;
#if LP_FLOAT
        c = tanf(filter->pidsr * filter->lkf);
#else
        c = tan(filter->pidsr * filter->lkf);
#endif
        
      filter->a[1] = 1.f / (1.f + (lpfloat_t)ROOT2 * c + c * c);
      filter->a[2] = -(filter->a[1] + filter->a[1]);
      filter->a[3] = filter->a[1];
      filter->a[4] = 2.f * (c*c - 1.f) * filter->a[1];
      filter->a[5] = (1.f - (lpfloat_t)ROOT2 * c + c * c) * filter->a[1];
    }

    t = in - filter->a[4] * filter->a[6] - filter->a[5] * filter->a[7];
    y = t * filter->a[1] + filter->a[2] * filter->a[6] + filter->a[3] * filter->a[7];
    filter->a[7] = filter->a[6];
    filter->a[6] = t;
    out = y;

    return out;
}

lpbfilter_t * fx_buttlp_create(lpfloat_t cutoff, lpfloat_t samplerate) {
    lpbfilter_t * filter = LPMemoryPool.alloc(1, sizeof(lpbfilter_t));
    memset(filter, 0, sizeof(lpbfilter_t));

    filter->sr = samplerate;
    filter->freq = cutoff;
    filter->pidsr = (lpfloat_t)PI / samplerate;

    return filter;
}

lpfloat_t fx_buttlp(lpbfilter_t * filter, lpfloat_t in) {
    lpfloat_t t, y, c, out = 0.f;

    if(filter->freq <= 0.f) return 0.f;

    if(filter->freq != filter->lkf) {
        filter->lkf = filter->freq;
#if LP_FLOAT
        c = 1.f / tanf(filter->pidsr * filter->lkf);
#else
        c = 1.f / tan(filter->pidsr * filter->lkf);
#endif
        
      filter->a[1] = 1.f / (1.f + (lpfloat_t)ROOT2 * c + c * c);
      filter->a[2] = filter->a[1] + filter->a[1];
      filter->a[3] = filter->a[1];
      filter->a[4] = 2.f * (1.f - c*c) * filter->a[1];
      filter->a[5] = (1.f - (lpfloat_t)ROOT2 * c + c * c) * filter->a[1];
    }

    t = in - filter->a[4] * filter->a[6] - filter->a[5] * filter->a[7];
    y = t * filter->a[1] + filter->a[2] * filter->a[6] + filter->a[3] * filter->a[7];
    filter->a[7] = filter->a[6];
    filter->a[6] = t;
    out = y;

    return out;
}

/* Crossover distortion ported from the supercollider CrossoverDistortion ugen */
lpfloat_t fx_crossover(lpfloat_t val, lpfloat_t amount, lpfloat_t smooth, lpfloat_t fade) {
    lpfloat_t out;
    out = lpfabs(val) - amount;
    if(out < 0.f) out *= (1.f + (out*fade)) * smooth;
    if(val < 0.f) out *= -1.f;
    return out;
}

/* Adapted from https://ccrma.stanford.edu/~jatin/ComplexNonlinearities/Wavefolder.html */
lpfloat_t fx_fold(lpfloat_t val, lpfloat_t * prev, lpfloat_t samplerate) {
    lpfloat_t out = 0;
#if LP_FLOAT
    lpfloat_t z = tanhf(val) + (tanhf(*prev) * 0.9f);
    out = z + (-0.5f * sinf(2.f * (float)PI * val * (samplerate/2.f) / samplerate));
#else
    lpfloat_t z = tanh(val) + (tanh(*prev) * 0.9f);
    out = z + (-0.5f * sin(2.f * (lpfloat_t)PI * val * (samplerate/2.f) / samplerate));
#endif
    *prev = out;
    return out;
}

lpfloat_t fx_limit(lpfloat_t val, lpfloat_t * prev, lpfloat_t threshold, lpfloat_t release, lpbuffer_t * del) {
    /* FIXME clean up generated code */
    lpfloat_t alpha, out, sample, absample, smoothgain, gain=1.f;
    int sample_idx;

#if DEBUG
    assert(del->channels == 1);
    assert(del->samplerate > 0);
#endif

    alpha = exp(-1.f / del->samplerate * release);
    sample_idx = (del->pos - 100 + del->length) % del->length; // 100 sample delay
    sample = del->data[sample_idx];

    absample = fabs(sample);    
    if(absample > threshold) gain = threshold / absample;

    smoothgain = alpha * (*prev) + (1.f - alpha) * gain;
    *prev = smoothgain;
    out = smoothgain * val;

    del->data[del->pos] = val;
    del->pos = (del->pos + 1) % del->length;

    return out;
}

void fx_norm(lpbuffer_t * buf, lpfloat_t ceiling) {
    lpfloat_t maxval, normval;
    size_t i;
    int c;

    maxval = mag_buffer(buf);
    if(maxval < 1e-10) return; // Avoid dividing by small values and creating
                               // Inf
    normval = ceiling / maxval;

    for(i=0; i < buf->length; i++) {
        for(c=0; c < buf->channels; c++) {
            buf->data[i * buf->channels + c] *= normval;
        }
    }
}

lpfloat_t fx_crush(lpfloat_t val, int bits) {
    size_t intmax = 0;
    lpfloat_t out = val;

    if(bits <= 0) return 0.f;
    
    intmax = pow(2, bits);
    out *= intmax;
    out = (lpfloat_t)((int)out); 
    out /= (lpfloat_t)intmax;

    return out;
}

lpbalance_t * fx_create_balancer(lpfloat_t samplerate) {
    lpfloat_t b;
    lpbalance_t * bal = LPMemoryPool.alloc(1, sizeof(lpbalance_t));
    bal->ihp = 10;
#if LP_FLOAT
    b = 2.f - cosf((lpfloat_t)(bal->ihp * (2.f * (lpfloat_t)PI / samplerate)));
    bal->c2 = b - sqrtf(b*b - 1.f);
#else
    b = 2.0 - cos((lpfloat_t)(bal->ihp * (2.0 * PI / samplerate)));
    bal->c2 = b - sqrt(b*b - 1.0);
#endif
    bal->c1 = 1.f - bal->c2;
    bal->prvq = bal->prvr = bal->prva = 0.f;

    return bal;
}

/*
 * The fx_balance routine was ported directly from Paul Batchelor's Soundpipe, 
 * in turn ported from the csound opcode.
 *
 * RIP Barry Vercoe.
 *
 * The original Soundpipe annotation is preserved below.
 *
 * This code has been extracted from the Csound opcode "balance".
 * It has been modified to work as a Soundpipe module.
 *
 * Original Author(s): Barry Vercoe, john ffitch, Gabriel Maldonado
 * Year: 1991
 * Location: OOps/ugens5.c
 */
lpfloat_t fx_balance(lpbalance_t * bal, lpfloat_t val, lpfloat_t reference) {
    lpfloat_t q, r, a, diff;
    lpfloat_t c1 = bal->c1;
    lpfloat_t c2 = bal->c2;
    lpfloat_t out = 0;

    q = bal->prvq;
    r = bal->prvr;
    lpfloat_t as = val;
    lpfloat_t cs = reference;

    q = c1 * as * as + c2 * q;
    r = c1 * cs * cs + c2 * r;

    bal->prvq = q;
    bal->prvr = r;

#if LP_FLOAT
    if(q != 0.f) {
        a = sqrtf(r/q);
    } else {
        a = sqrtf(r);
    }
#else
    if(q != 0.0) {
        a = sqrt(r/q);
    } else {
        a = sqrt(r);
    }
#endif

    if((diff = a - bal->prva) != 0.f) {
        out = val * bal->prva;
        bal->prva = a;
    } else {
        out = val * a;
    }

    return out;
}

void fx_destroy_balancer(lpbalance_t * bal) {
    LPMemoryPool.free(bal);
}

lpbuffer_t * fx_crossfade(lpbuffer_t * a, lpbuffer_t * b, lpbuffer_t * curve) {
    size_t i, smaller_length=(a->length > b->length) ? b->length : a->length;
    lpfloat_t pos, p;
    int c, min_channels=(a->channels > b->channels) ? b->channels : a->channels;
    lpbuffer_t * out = LPBuffer.create(smaller_length, min_channels, a->samplerate);

    for(i=0; i < smaller_length; i++) {
        pos = (lpfloat_t)i / smaller_length;
        p = LPInterpolation.linear_pos(curve, pos);
        for(c=0; c < min_channels; c++) {
            out->data[i * min_channels + c] = (a->data[i * min_channels + c] * p) + (b->data[i * min_channels + c] * (1.f-p));
        }
    }

    return out;
}

lpfloat_t fx_multifade(lpbuffer_t * buf, lpfloat_t pos, lpfloat_t pan, int method) {
    /* Crossfade across multiple channels based on pan position (0-1)
     *
     * Args:
     *   buf: multichannel buffer to read from
     *   pos: read position (0-1) within the buffer
     *   pan: pan position from 0 (first channel) to 1 (last channel)
     *   method: PANMETHOD_CONSTANT for constant power, PANMETHOD_LINEAR for linear
     *
     * Returns:
     *   Single crossfaded sample value
     *
     * Example:
     *   3-channel buffer:
     *     pan=0.0   -> 100% channel 0
     *     pan=0.5   -> 100% channel 1
     *     pan=1.0   -> 100% channel 2
     *     pan=0.25  -> 50% channel 0, 50% channel 1
     */
    lpfloat_t phase, frac, a, b, amp_a, amp_b;
    int channel_a, channel_b;

    if(buf->channels <= 0) return 0.f;
    if(buf->channels == 1) return interpolate_linear_pos(buf, pos);
    if(pos < 0.f || pos > 1.f) return 0.f;

    /* Clamp pan to 0-1 */
    if(pan < 0.f) pan = 0.f;
    if(pan > 1.f) pan = 1.f;

    /* Map pan position to channel space */
    phase = pan * (buf->channels - 1);
    channel_a = (int)phase;
    channel_b = channel_a + 1;

    /* Clamp channel indices */
    if(channel_a >= buf->channels) channel_a = buf->channels - 1;
    if(channel_b >= buf->channels) channel_b = buf->channels - 1;

    frac = phase - channel_a;

    /* Read samples from adjacent channels using interpolation */
    a = interpolate_linear_channel(buf, pos, channel_a);
    b = interpolate_linear_channel(buf, pos, channel_b);

    /* Calculate crossfade amplitudes */
    if(method == PANMETHOD_CONSTANT) {
        /* Constant power crossfade */
        amp_a = sqrt(1.f - frac);
        amp_b = sqrt(frac);
    } else {
        /* Linear crossfade */
        amp_a = 1.f - frac;
        amp_b = frac;
    }

    return (a * amp_a) + (b * amp_b);
}

void fx_diffuse(lpbuffer_t * out, size_t frame, lpfloat_t sample, lpfloat_t pan, int method) {
    /* Diffuse a mono sample across a multichannel output space.
     *
     * Args:
     *   out: multichannel output buffer to write to
     *   frame: frame index to write
     *   sample: mono sample value to diffuse
     *   pan: pan position from 0 (first channel) to 1 (last channel)
     *   method: PANMETHOD_CONSTANT for constant power, PANMETHOD_LINEAR for linear
     *
     * Example:
     *   3-channel output:
     *     pan=0.0   -> 100% to channel 0
     *     pan=0.5   -> 100% to channel 1
     *     pan=1.0   -> 100% to channel 2
     *     pan=0.25  -> 50% to channel 0, 50% to channel 1
     */
    lpfloat_t phase, frac, amp_a, amp_b;
    int channel_a, channel_b, c;

    if(out->channels <= 0 || frame >= out->length) return;

    /* Single channel - just write directly */
    if(out->channels == 1) {
        out->data[frame] = sample;
        return;
    }

    /* Clamp pan to 0-1 */
    if(pan < 0.f) pan = 0.f;
    if(pan > 1.f) pan = 1.f;

    /* Map pan position to channel space */
    phase = pan * (out->channels - 1);
    channel_a = (int)phase;
    channel_b = channel_a + 1;

    /* Clamp channel indices */
    if(channel_a >= out->channels) channel_a = out->channels - 1;
    if(channel_b >= out->channels) channel_b = out->channels - 1;

    frac = phase - channel_a;

    /* Calculate crossfade amplitudes */
    if(method == PANMETHOD_CONSTANT) {
        /* Constant power panning */
        amp_a = sqrt(1.f - frac);
        amp_b = sqrt(frac);
    } else {
        /* Linear panning */
        amp_a = 1.f - frac;
        amp_b = frac;
    }

    /* Clear all channels for this frame first */
    for(c = 0; c < out->channels; c++) {
        out->data[frame * out->channels + c] = 0.f;
    }

    /* Write to adjacent channels with appropriate amplitudes */
    out->data[frame * out->channels + channel_a] = sample * amp_a;
    if(channel_a != channel_b) {
        out->data[frame * out->channels + channel_b] = sample * amp_b;
    }
}

void fx_diffuse_into(lpbuffer_t * out, size_t frame, lpfloat_t sample, lpfloat_t pan, int method) {
    /* Diffuse a mono sample into a multichannel output space (mix, don't overwrite).
     *
     * Args:
     *   out: multichannel output buffer to mix into
     *   frame: frame index to write
     *   sample: mono sample value to diffuse
     *   pan: pan position from 0 (first channel) to 1 (last channel)
     *   method: PANMETHOD_CONSTANT for constant power, PANMETHOD_LINEAR for linear
     *
     * Example:
     *   3-channel output:
     *     pan=0.0   -> 100% to channel 0
     *     pan=0.5   -> 100% to channel 1
     *     pan=1.0   -> 100% to channel 2
     *     pan=0.25  -> 50% to channel 0, 50% to channel 1
     */
    lpfloat_t phase, frac, amp_a, amp_b;
    int channel_a, channel_b;

    if(out->channels <= 0 || frame >= out->length) return;

    /* Single channel - just mix directly */
    if(out->channels == 1) {
        out->data[frame] += sample;
        return;
    }

    /* Clamp pan to 0-1 */
    if(pan < 0.f) pan = 0.f;
    if(pan > 1.f) pan = 1.f;

    /* Map pan position to channel space */
    phase = pan * (out->channels - 1);
    channel_a = (int)phase;
    channel_b = channel_a + 1;

    /* Clamp channel indices */
    if(channel_a >= out->channels) channel_a = out->channels - 1;
    if(channel_b >= out->channels) channel_b = out->channels - 1;

    frac = phase - channel_a;

    /* Calculate crossfade amplitudes */
    if(method == PANMETHOD_CONSTANT) {
        /* Constant power panning */
        amp_a = sqrt(1.f - frac);
        amp_b = sqrt(frac);
    } else {
        /* Linear panning */
        amp_a = 1.f - frac;
        amp_b = frac;
    }

    /* Mix into adjacent channels with appropriate amplitudes */
    out->data[frame * out->channels + channel_a] += sample * amp_a;
    if(channel_a != channel_b) {
        out->data[frame * out->channels + channel_b] += sample * amp_b;
    }
}

void fx_convolve(lpbuffer_t * a, lpbuffer_t * b, lpbuffer_t * out) {
    int c;
    size_t i, j;
    lpfloat_t maxval;

#if DEBUG
    assert(a->channels == b->channels);
    assert(a->channels == out->channels);
    assert(out->length == a->length + b->length + 1);
#endif

    maxval = mag_buffer(a);

    for(i=0; i < a->length; i++) {
        for(c=0; c < a->channels; c++) {
            for(j=0; j < b->length; j++) {
                out->data[(j+i) * a->channels + c] += a->data[i * a->channels + c] * b->data[j * a->channels + c];
            }
        }
    }

    fx_norm(out, maxval);
}


/* RingBuffers
 */
lpbuffer_t * ringbuffer_create(size_t length, int channels, int samplerate) {
    lpbuffer_t * ringbuf;
    ringbuf = LPBuffer.create(length, channels, samplerate);
    ringbuf->pos = 0;
    ringbuf->boundary = length - 1;
    return ringbuf;
}

void ringbuffer_fill(lpbuffer_t * ringbuf, lpbuffer_t * buf, int offset) {
    size_t i;
    int c;
    size_t pos = ringbuf->pos - buf->length - offset;
    pos = pos % ringbuf->length;
    for(i=0; i < buf->length; i++) {
        for(c=0; c < ringbuf->channels; c++) {
            buf->data[i * buf->channels + c] = ringbuf->data[pos * ringbuf->channels + c];
        }

        pos += 1;
        pos = pos % ringbuf->length;
    }
}

lpfloat_t ringbuffer_readone(lpbuffer_t * ringbuf, int offset) {
    return ringbuf->data[(ringbuf->pos - offset) % ringbuf->length];
}

void ringbuffer_readinto(lpbuffer_t * ringbuf, lpfloat_t * data, size_t length, int channels) {
    size_t i;
    int c;
    size_t pos = ringbuf->pos - length;
    pos = pos % ringbuf->length;

    for(i=0; i < length; i++) {
        for(c=0; c < channels; c++) {
            data[i * channels + c] = ringbuf->data[pos * channels + c];
        }

        pos += 1;
        pos = pos % ringbuf->length;
    }
}

lpbuffer_t * ringbuffer_read(lpbuffer_t * ringbuf, size_t length) {
    size_t i;
    int c;
    size_t pos = ringbuf->pos - length;
    lpbuffer_t * out;

    pos = pos % ringbuf->length;
    out = LPBuffer.create(length, ringbuf->channels, ringbuf->samplerate);
    for(i=0; i < length; i++) {
        for(c=0; c < ringbuf->channels; c++) {
            out->data[i * out->channels + c] = ringbuf->data[pos * ringbuf->channels + c];
        }

        pos += 1;
        pos = pos % ringbuf->length;
    }

    return out;
}

void ringbuffer_writeone(lpbuffer_t * ringbuf, lpfloat_t sample) {
    ringbuf->data[ringbuf->pos] = sample;
    ringbuf->pos += 1;
    ringbuf->pos = ringbuf->pos % ringbuf->length;
}

void ringbuffer_writefrom(lpbuffer_t * ringbuf, lpfloat_t * data, size_t length, int channels) {
    size_t i;
    int c, j;
    for(i=0; i < length; i++) {
        for(c=0; c < ringbuf->channels; c++) {
            j = c % channels;
            ringbuf->data[ringbuf->pos * ringbuf->channels + c] = data[i * channels + j];
        }

        ringbuf->pos += 1;
        ringbuf->pos = ringbuf->pos % ringbuf->length;
    }
}

void ringbuffer_write(lpbuffer_t * ringbuf, lpbuffer_t * buf) {
    size_t i;
    int c, j;
    for(i=0; i < buf->length; i++) {
        for(c=0; c < ringbuf->channels; c++) {
            j = c % buf->channels;
            ringbuf->data[ringbuf->pos * ringbuf->channels + c] = buf->data[i * buf->channels + j];
        }

        ringbuf->pos += 1;
        ringbuf->pos = ringbuf->pos % ringbuf->length;
    }
}

void ringbuffer_dub(lpbuffer_t * buf, lpbuffer_t * src) {
    size_t i;
    int c, j;
    for(i=0; i < src->length; i++) {
        for(c=0; c < buf->channels; c++) {
            j = c % src->channels;
            buf->data[buf->pos * buf->channels + c] += src->data[i * src->channels + j];
        }

        buf->pos += 1;
        buf->pos = buf->pos % buf->length;
    }
}

void ringbuffer_destroy(lpbuffer_t * buf) {
    LPBuffer.destroy(buf);
}


/* LPMemoryPool
 * */
void memorypool_init(unsigned char * pool, size_t poolsize) {
#if DEBUG
    assert(poolsize >= 1);
#endif
    LPMemoryPool.pool = pool;
    LPMemoryPool.poolsize = poolsize;
    LPMemoryPool.pos = 0;
}

lpmemorypool_t * memorypool_custom_init(unsigned char * pool, size_t poolsize) {
    lpmemorypool_t * mp;
    mp = (lpmemorypool_t *)LPMemoryPool.alloc(1, sizeof(lpmemorypool_t));

#if DEBUG
    assert(poolsize >= 1);
#endif
    mp->pool = pool;
    mp->poolsize = poolsize;
    mp->pos = 0;

    return mp;
}

void * memorypool_custom_alloc(lpmemorypool_t * mp, size_t itemcount, size_t itemsize) {
    void * p;
    size_t length;

#if DEBUG
    assert(mp->pool != 0); 
#endif

    length = itemcount * itemsize;

    if(mp->poolsize >= mp->pos + length) {
        p = (void *)(&mp->pool[mp->pos]);
        mp->pos += length;
        return p;
    }
    /* FIXME might as well try to expand the pool here */
    //exit(EXIT_FAILURE);
    return NULL;
}

#ifdef LP_STATIC
// Simple arena allocator
void * memorypool_alloc(size_t itemcount, size_t itemsize) {
    void * p;
    size_t size;
    size = itemcount * itemsize;

#if DEBUG
    assert(LPMemoryPool.pool != 0); 
#endif

    if(LPMemoryPool.poolsize >= LPMemoryPool.pos + size) {
        p = (void *)(&LPMemoryPool.pool[LPMemoryPool.pos]);
        LPMemoryPool.pos += size;
        return p;
    }
    return NULL;
}
void memorypool_free(void * ptr) {
    // When LP_STATIC is defined, void the pointer so that 
    // lifecycle checks for NULL still work, but a
    // future memorypool implementation could try to 
    // make more room in the arena here?
    (void)ptr;
}

#else
// Calloc wrapper
void * memorypool_alloc(size_t itemcount, size_t itemsize) {
    void * p;
    p = (void *)calloc(itemcount, itemsize);

#if 0
    // look up the memory alignment size, or fallback to 16bits
    int align_size = sysconf(_SC_LEVEL1_DCACHE_LINESIZE);
    if (align_size == -1) {
        align_size = sysconf(_SC_PAGESIZE);
        if (align_size == -1) {
            align_size = 16;
        }
    }

    if(posix_memalign(&p, align_size, itemcount * itemsize) < 0) {
        fprintf(stderr, "Memory alignment failure during alloc of %d bytes. %s (%d)\n", (int)(itemcount * itemsize), strerror(errno), errno);
        exit(EXIT_FAILURE);
    }
#endif
    if(p == NULL) {
        fprintf(stderr, "Calloc returned null trying to alloc %d bytes. %s (%d)\n", (int)(itemcount * itemsize), strerror(errno), errno);
        return NULL;
    }
    return p;
}

void memorypool_free(void * ptr) {
    free(ptr);
}
#endif

/* Param
 * TODO add option for using a static buffer -- never alloc here
 * lpbuffer_t foo = {.data={[7]=0}}; for an 8 channel max buffer?
 * */
lpbuffer_t * param_create_from_float(lpfloat_t value) {
    lpbuffer_t * param = create_buffer(1, 1, DEFAULT_SAMPLERATE);
    param->data[0] = value;
    return param;
}

lpbuffer_t * param_create_from_int(int value) {
    lpbuffer_t * param = create_buffer(1, 1, DEFAULT_SAMPLERATE);
    param->data[0] = (lpfloat_t)value;
    return param;
}

/* This smoother was ported from sndkit with 
 * minimal changes. Thanks, Paul! 
 *
 * The implementation is explained in detail here:
 *     https://pbat.ch/sndkit/smoother/
 */
lpsmoother_t param_smoother_create(lpfloat_t samplerate) {
    lpsmoother_t smoother = {0};
    smoother.smooth = .00033f;
    smoother.psmooth = -1;
    smoother.onedsr = 1.f/samplerate;
    return smoother;
}

void param_smoother_update_samplerate(lpsmoother_t * smoother, lpfloat_t samplerate) {
    smoother->onedsr = 1.f/samplerate;
}

void param_smoother_snap_to_value(lpsmoother_t * smoother, lpfloat_t value) {
    smoother->y0 = value;
}

lpfloat_t param_smooth(lpsmoother_t * s, lpfloat_t value) {
    lpfloat_t out = 0.f;

    if(s->psmooth != s->smooth) {
        s->a1 = pow(0.5f, s->onedsr/s->smooth);
        //s->a1 = expf(-s->onedsr/s->smooth);
        s->b0 = 1.f - s->a1;
        s->psmooth = s->smooth;
    }

    s->y0 = s->b0 * value + s->a1 * s->y0;
    out = s->y0;

    return out;
}

/* Interpolation
 * */
lpfloat_t interpolate_hermite(lpbuffer_t* buf, lpfloat_t phase) {
    lpfloat_t y0, y1, y2, y3, frac;
    lpfloat_t c0, c1, c2, c3;
    int i0, i1, i2, i3;

    if(buf->range == 1) return buf->data[0];
    if(buf->range < 1) return 0;

    frac = phase - (int)phase;
    i1 = (int)phase;
    i2 = i1 + 1;
    i3 = i2 + 1;
    i0 = i1 - 1;

    y0 = 0;
    y1 = 0;
    y2 = 0;
    y3 = 0;

    if(i0 >= 0) y0 = buf->data[i0];
    if(i1 <= (int)buf->boundary) y1 = buf->data[i1];
    if(i2 <= (int)buf->boundary) y2 = buf->data[i2];
    if(i3 <= (int)buf->boundary) y3 = buf->data[i3];

    /* This part was taken from version #2 by James McCartney 
     * https://www.musicdsp.org/en/latest/Other/93-hermite-interpollation.html
     */
    c0 = y1;
    c1 = 0.5f * (y2 - y0);
    c3 = 1.5f * (y1 - y2) + 0.5f * (y3 - y0);
    c2 = y0 - y1 + c1 - c3;
    return ((c3 * frac + c2) * frac + c1) * frac + c0;
}

lpfloat_t interpolate_hermite_pos(lpbuffer_t* buf, lpfloat_t pos) {
    return interpolate_hermite(buf, pos * buf->length);
}

/* Interpolated read from a multichannel buffer
 */
lpfloat_t interpolate_linear_channel(lpbuffer_t* buf, lpfloat_t phase, int channel) {
    lpfloat_t frac, a, b;
    size_t i;

    if(buf->range == 1) return buf->data[0];
    
    frac = phase - (int)phase;
    i = (int)phase;

    if(i > buf->boundary) return buf->data[buf->boundary];

    a = buf->data[i * buf->channels + channel];
    b = buf->data[(i+1) * buf->channels + channel];

    return (1.0f - frac) * a + (frac * b);
}

/* Bandlimited interpolation by Liquid City Motors Will 
 * In-progress port from cython 2025 by hcj
 * */
lpbli_t * interpolate_bli_create(int quality, int loop) {
    int i;
    lpfloat_t sample;
    lpbli_t * bli = (lpbli_t*)LPMemoryPool.alloc(1, sizeof(lpbli_t));

    bli->quality = quality;
    bli->samples_per_0x = 512;
    bli->filter_length = quality * bli->samples_per_0x;

    if(loop) {
        bli->wrap = 1;
    } else {
        bli->wrap = 0;
    }

    /* FIXME -- this ignores the quality param...
    sinc_domain = np.linspace(0, bli.quality, bli.filter_length)
    sinc_sample = np.sinc(sinc_domain)
    window = np.blackman(bli.filter_length * 2)[bli.filter_length:]
    sinc_sample *= window
    */

    lpbuffer_t * win = LPWindow.create(WIN_SINC, bli->filter_length);
    lpbuffer_t * blacwin = LPWindow.create(WIN_BLACK, bli->filter_length);
    LPBuffer.multiply(win, blacwin);

    bli->filter_table = (lpfloat_t*)LPMemoryPool.alloc(bli->filter_length + 1, sizeof(lpfloat_t));
    for(i=0; i < bli->filter_length; i++) {
        sample = win->data[i];
        bli->filter_table[i] = sample;
    }

    bli->filter_table[bli->filter_length] = 0;

    return bli;
}

lpfloat_t interpolate_bli_get_filter_coeff(lpbli_t * bli, lpfloat_t pos) {
    lpfloat_t expanded_phase = pos * bli->samples_per_0x;
    int left_index = (int)expanded_phase;
    int right_index = left_index + 1;
    lpfloat_t fractional_part = expanded_phase - left_index;
    return bli->filter_table[left_index] * (1 - fractional_part) + bli->filter_table[right_index] * fractional_part;
}

void interpolate_bli_destroy(lpbli_t * bli) {
    LPMemoryPool.free(bli->filter_table);
    LPMemoryPool.free(bli);
}

lpfloat_t interpolate_bli(lpbli_t * bli, lpbuffer_t * buf, lpfloat_t phase) {
    int table_length = bli->table_length;
    lpfloat_t resampling_factor = bli->resampling_factor;

    int wrap = bli->wrap * (table_length - 1);
    wrap += 1;
    
    int left_index = (int)phase;
    int right_index = (left_index + 1);
    if(right_index >= table_length) {
        right_index -= wrap;
    }

    lpfloat_t fractional_part = phase - left_index;

    if(resampling_factor > 1) { resampling_factor = 1; }

    /* start the accumulation */
    lpfloat_t sample = 0;

    /* apply the left hand side of the filter on "past wavetable samples"
     * tricky, the first lookup in the filter is the fractional part scaled down by the resampling factor */
    lpfloat_t filter_phasor = fractional_part * resampling_factor;

    /* first sample on the chopping block is the left neighbor */
    int read_index = left_index;

    lpfloat_t coeff = 0;

    while (filter_phasor < bli->quality) {
        /* get the interpolated coefficient */
        coeff = interpolate_bli_get_filter_coeff(bli, filter_phasor);
        /* increment through the filter indices by the resampling factor */
        filter_phasor += resampling_factor;
        /* for each stop in the filter table, burn a new sample value */
        sample += coeff * buf->data[read_index];
        /* next sample on the chopping block is the previous one */
        read_index -= 1;
        if (read_index < 0) {
            read_index += wrap;
        }
    }

    /* apply the right hand side of the filter on "future wavetable samples"
     * tricky, the first lookup in the filter is 1 - the fractional part scaled down by the resampling factor */
    filter_phasor = (1 - fractional_part) * resampling_factor;
    /* pretty much same as the other wing but we move forward through the wavetable at each new coefficient */
    read_index = right_index;

    while (filter_phasor < bli->quality) {
        coeff = interpolate_bli_get_filter_coeff(bli, filter_phasor);
        filter_phasor += resampling_factor;
        sample += coeff * buf->data[read_index];
        read_index += 1;
        if (read_index >= table_length) {
            read_index -= wrap;
        }
    }

    return sample * resampling_factor;
}

lpfloat_t interpolate_bli_pos(lpbli_t * bli, lpbuffer_t * buf, lpfloat_t pos) {
    return interpolate_bli(bli, buf, pos * buf->length);
}

lpfloat_t interpolate_trunc(lpbuffer_t * buf, lpfloat_t phase) {
    size_t i;

    if(buf->range == 1) return buf->data[0];

    i = (size_t)phase;
    if(i > buf->boundary) return buf->data[buf->boundary];
    return buf->data[i];
}

lpfloat_t interpolate_trunc_pos(lpbuffer_t* buf, lpfloat_t pos) {
    return interpolate_trunc(buf, pos * buf->length);
}

lpfloat_t interpolate_linear(lpbuffer_t * buf, lpfloat_t phase) {
    lpfloat_t frac, a, b;
    size_t i;

    if(buf->range == 1) return buf->data[0];

    frac = phase - (int)phase;
    i = (int)phase;

    if(i >= buf->boundary) return buf->data[buf->boundary];

    a = buf->data[i];
    b = buf->data[i+1];

    return (1.0f - frac) * a + (frac * b);
}

lpfloat_t interpolate_linear_pos(lpbuffer_t* buf, lpfloat_t pos) {
    return interpolate_linear(buf, pos * buf->length);
}

lpfloat_t interpolate_linear_pos2(lpfloat_t * buf, size_t length, lpfloat_t pos) {
    lpfloat_t frac, a, b, phase;
    size_t i;

    phase = pos * length;

    if(length == 1) return buf[0];
    
    frac = phase - (int)phase;
    i = (int)phase;

    if (i >= length-1) return 0;

    a = buf[i];
    b = buf[i+1];

    return (1.0f - frac) * a + (frac * b);
}

/* Wavetable generators
 * 
 * All these functions return a table of values 
 * of the given length with values between -1 and 1
 */
void wavetable_sine(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = sin((i/(lpfloat_t)length) * (lpfloat_t)PI * 2.0f);
    }
}

void wavetable_cosine(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = cos((i/(lpfloat_t)length) * (lpfloat_t)PI * 2.0f);
    }
}

void wavetable_square(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        if(i < (length/2.0f)) {
            out[i] = 0.9999f;
        } else {
            out[i] = -0.9999f;
        }
    }
}

void wavetable_tri(lpfloat_t* out, int length) {
    int i;
    int offset = (int)(length * 0.25f);
    for(i=0; i < length; i++) {
        out[(i+offset) % length] = (lpfloat_t)fabs((i/(lpfloat_t)length) * 2.0f - 1.0f) * 2.0f - 1.0f;
    }
}

void wavetable_tri2(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = (lpfloat_t)fabs((i/(lpfloat_t)length) * 2.0f - 1.0f) * 2.0f - 1.0f;
    }
}

void wavetable_saw(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = (i/(lpfloat_t)length) * 2.f - 1.f;
    }
}

void wavetable_rsaw(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = (1.f - i/(lpfloat_t)length) * 2.f - 1.f;
    }
}

/* create a wavetable (-1 to 1) */
lpbuffer_t* create_wavetable(int name, size_t length) {
    /* Handle WT_RND first to avoid allocating a buffer that we'll leak */
    if (name == WT_RND) {
        return create_wavetable(rand_choice(NUM_WAVETABLES), length);
    }

    lpbuffer_t* buf = LPBuffer.create(length, 1, DEFAULT_SAMPLERATE);
    if(name == WT_SINE) {
        wavetable_sine(buf->data, length);
    } else if (name == WT_COS) {
        wavetable_cosine(buf->data, length);
    } else if (name == WT_TRI) {
        wavetable_tri(buf->data, length);
    } else if (name == WT_TRI2) {
        wavetable_tri2(buf->data, length);
    } else if (name == WT_SQUARE) {
        wavetable_square(buf->data, length);
    } else if (name == WT_SAW) {
        wavetable_saw(buf->data, length);
    } else if (name == WT_RSAW) {
        wavetable_rsaw(buf->data, length);
    } else {
        wavetable_sine(buf->data, length);
    }
    return buf;
}

lpbuffer_t * lpbuffer_create_stack(lpbuffer_t * (*table_creator)(int name, size_t length), int numtables, size_t * onsets, size_t * lengths, va_list vl) {
    lpbuffer_t * stack;
    lpbuffer_t * user_bufp;
    int i;
    size_t tablesize, stacklength, pos, j;
    lpbuffer_t ** bufs;
    size_t * tablesizes;
    int * tables;

    bufs = (lpbuffer_t **)LPMemoryPool.alloc(numtables, sizeof(lpbuffer_t *));
    tablesizes = (size_t *)LPMemoryPool.alloc(numtables, sizeof(size_t));
    tables = (int *)LPMemoryPool.alloc(numtables, sizeof(int));

    memset(bufs, 0, numtables * sizeof(lpbuffer_t *));
    memset(tablesizes, 0, numtables * sizeof(size_t));
    memset(tables, 0, numtables * sizeof(int));

    stacklength = 0;

    // first pass get all sizes
    for(i=0; i < numtables; i++) {
        tables[i] = va_arg(vl, int);
        if(tables[i] == WT_USER) {
            user_bufp = va_arg(vl, lpbuffer_t *);
            tablesizes[i] = user_bufp->length;
            bufs[i] = LPBuffer.clone(user_bufp);
            stacklength += tablesizes[i];
        } else {
            tablesize = va_arg(vl, int);
            stacklength += tablesize;
            tablesizes[i] = tablesize;
        }
    }

    stack = LPBuffer.create(stacklength, 1, DEFAULT_SAMPLERATE);
    if(stack == NULL) return NULL;

    pos = 0;
    for(i=0; i < numtables; i++) {
        if(tables[i] != WT_USER) {
            bufs[i] = table_creator(tables[i], tablesizes[i]); 
        }

        for(j=0; j < bufs[i]->length; j++) {
            stack->data[j + pos] = bufs[i]->data[j];
        }

        onsets[i] = pos;
        lengths[i] = tablesizes[i];

        pos += bufs[i]->length;

        LPMemoryPool.free(bufs[i]);
    }

    LPMemoryPool.free(tables);
    LPMemoryPool.free(tablesizes);
    LPMemoryPool.free(bufs);

    return stack;
}

lpbuffer_t * create_wavetable_stack(int numtables, size_t * onsets, size_t * lengths, ...) {
    lpbuffer_t * stack;
    va_list vl;
    va_start(vl, lengths);
    va_end(vl);
    stack = lpbuffer_create_stack(create_wavetable, numtables, onsets, lengths, vl);
    return stack;
}

lpbuffer_t * create_window_stack(int numtables, size_t * onsets, size_t * lengths, ...) {
    lpbuffer_t * stack;
    va_list vl;
    va_start(vl, lengths);
    stack = lpbuffer_create_stack(create_window, numtables, onsets, lengths, vl);
    va_end(vl);
    return stack;
}


void destroy_wavetable(lpbuffer_t* buf) {
    LPBuffer.destroy(buf);
}


/* Window generators
 *
 * All these functions return a table of values 
 * of the given length with values between 0 and 1
 */
void window_phasor(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = i/(lpfloat_t)length;      
    }
}

void window_rsaw(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = 1.f - (i/(lpfloat_t)length);
    }
}

void window_tri(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = 1.0f - (lpfloat_t)fabs((i/(lpfloat_t)length) * 2.0f - 1.0f);
    }
}

void window_cosine(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = (lpfloat_t)cos((i/(lpfloat_t)length) * (lpfloat_t)PI);         
    }
}

void window_sine(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = (lpfloat_t)sin((i/(lpfloat_t)length) * (lpfloat_t)PI);         
    }
}

void window_sinein(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = (lpfloat_t)sin((i/(lpfloat_t)length) * (lpfloat_t)HALFPI);         
    }
}

void window_sineout(lpfloat_t* out, int length) {
    int i;
    for(i=0; i < length; i++) {
        out[i] = (lpfloat_t)sin(((i/(lpfloat_t)length) * (lpfloat_t)HALFPI) + (lpfloat_t)HALFPI);
    }
}

void window_pluckin(lpfloat_t * out, int length) {
    lpfloat_t frac, a, b, phase;
    int i, idx, reverse_idx;

    if(length <= 0) return;

    for(i=0; i < length; i++) {
        phase = ((lpfloat_t)i / (length - 1)) * (BUILTIN_WINDOW_SIZE - 1);
        frac = phase - (int)phase;
        idx = (int)phase;
        
        if(idx >= BUILTIN_WINDOW_SIZE - 1) {
            idx = BUILTIN_WINDOW_SIZE - 2;
            frac = 1.0f;
        }
        
        reverse_idx = BUILTIN_WINDOW_SIZE - 1 - idx;
        
        a = LPWIN_PLUCKOUT[reverse_idx];
        if(reverse_idx > 0) {
            b = LPWIN_PLUCKOUT[reverse_idx - 1];
        } else {
            b = LPWIN_PLUCKOUT[reverse_idx];
        }

        out[i] = (1.0f - frac) * a + (frac * b);
    }
}

void window_pluckout(lpfloat_t * out, int length) {
    lpfloat_t frac, a, b, phase;
    int i, idx;

    if(length <= 0) return;

    for(i=0; i < length; i++) {
        phase = ((lpfloat_t)i / (length - 1)) * (BUILTIN_WINDOW_SIZE - 1);
        frac = phase - (int)phase;
        idx = (int)phase;

        if(idx >= BUILTIN_WINDOW_SIZE - 1) {
            idx = BUILTIN_WINDOW_SIZE - 2;
            frac = 1.0f;
        }

        a = LPWIN_PLUCKOUT[idx];
        b = LPWIN_PLUCKOUT[idx + 1];

        out[i] = (1.0f - frac) * a + (frac * b);
    }
}


void window_hanning(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 1);
#endif
    for(i=0; i < length; i++) {
        out[i] = 0.5f - 0.5f * (lpfloat_t)cos(2.0f * (lpfloat_t)PI * i / (length-1.0f));
    }
}

void window_hannin(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    int double_length = length * 2;
    for(i=0; i < length; i++) {
        out[i] = 0.5f - 0.5f * (lpfloat_t)cos(2.0f * (lpfloat_t)PI * i / (double_length - 1.0f));
    }
}

void window_hannout(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    int double_length = length * 2;
    for(i=0; i < length; i++) {
        out[i] = 0.5f - 0.5f * (lpfloat_t)cos(2.0f * (lpfloat_t)PI * (i + length) / (double_length - 1.0f));
    }
}

void window_hamming(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    for(i=0; i < length; i++) {
        out[i] = 0.54f - 0.46f * (lpfloat_t)cos(2.0f * (lpfloat_t)PI * i / (length - 1.0f));
    }
}

void window_bartlett(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    if(length == 1) {
        out[0] = 1.0f;
        return;
    }
    
    for(i=0; i < length; i++) {
        if(i <= (length-1)/2) {
            out[i] = (2.0f * i) / (length - 1.0f);
        } else {
            out[i] = 2.0f - (2.0f * i) / (length - 1.0f);
        }
    }
}

void window_blackman(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    for(i=0; i < length; i++) {
        lpfloat_t cos2 = (lpfloat_t)cos(2.0f * (lpfloat_t)PI * i / (length - 1.0f));
        lpfloat_t cos4 = (lpfloat_t)cos(4.0f * (lpfloat_t)PI * i / (length - 1.0f));
        out[i] = 0.42f - 0.5f * cos2 + 0.08f * cos4;
    }
}

void window_sinc(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    for(i=0; i < length; i++) {
        lpfloat_t x = -15.0f + (30.0f * i) / (length - 1.0f);
        
        // FIXME fabs
        if((lpfloat_t)fabs(x) < 1e-10f) {
            out[i] = 1.0f;
        } else {
            lpfloat_t pi_x = (lpfloat_t)PI * x;
            out[i] = (lpfloat_t)sin(pi_x) / pi_x;
        }
    }
}

void window_gaussian(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    lpfloat_t nn = 0.5f * (length - 1);
    for(i=0; i < length; i++) {
        lpfloat_t ax = (i - nn) / (0.3f * nn);
        out[i] = (lpfloat_t)exp(-0.5f * ax * ax);
    }
}

void window_gaussin(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    for(i=0; i < length; i++) {
        lpfloat_t ax = ((lpfloat_t)(length - i) / (lpfloat_t)length) * 4.0f;
        out[i] = (lpfloat_t)exp(-0.5f * ax * ax);
    }
}

void window_gaussout(lpfloat_t* out, int length) {
    int i;
#if DEBUG
    assert(length > 0);
#endif
    for(i=0; i < length; i++) {
        lpfloat_t ax = ((lpfloat_t)i / (lpfloat_t)length) * 4.0f;
        out[i] = (lpfloat_t)exp(-0.5f * ax * ax);
    }
}

/* create a window (0 to 1) */
lpbuffer_t * create_window(int name, size_t length) {
    /* Handle WIN_RND first to avoid allocating a buffer that we'll leak */
    if (name == WIN_RND) {
        return create_window(rand_choice(NUM_WINDOWS), length);
    }

    lpbuffer_t* buf = LPBuffer.create(length, 1, DEFAULT_SAMPLERATE);
    if(name == WIN_NONE) {
        memset(buf->data, 1.f, length * sizeof(lpfloat_t));
    } else if(name == WIN_SINE) {
        window_sine(buf->data, length);
    } else if (name == WIN_SINEIN) {
        window_sinein(buf->data, length);
    } else if (name == WIN_SINEOUT) {
        window_sineout(buf->data, length);
    } else if (name == WIN_COS) {
        window_cosine(buf->data, length);
    } else if (name == WIN_TRI) {
        window_tri(buf->data, length);
    } else if (name == WIN_PHASOR) {
        window_phasor(buf->data, length);
    } else if (name == WIN_HANN) {
        window_hanning(buf->data, length);
    } else if (name == WIN_HANNIN) {
        window_hannin(buf->data, length);
    } else if (name == WIN_HANNOUT) {
        window_hannout(buf->data, length);
    } else if (name == WIN_HAMM) {
        window_hamming(buf->data, length);
    } else if (name == WIN_BART) {
        window_bartlett(buf->data, length);
    } else if (name == WIN_BLACK) {
        window_blackman(buf->data, length);
    } else if (name == WIN_SINC) {
        window_sinc(buf->data, length);
    } else if (name == WIN_GAUSS) {
        window_gaussian(buf->data, length);
    } else if (name == WIN_GAUSSIN) {
        window_gaussin(buf->data, length);
    } else if (name == WIN_GAUSSOUT) {
        window_gaussout(buf->data, length);
    } else if (name == WIN_SAW) {
        window_phasor(buf->data, length);
    } else if (name == WIN_RSAW) {
        window_rsaw(buf->data, length);
    } else if (name == WIN_PLUCKIN) {
        window_pluckin(buf->data, length);
    } else if (name == WIN_PLUCKOUT) {
        window_pluckout(buf->data, length);
    } else {
        window_sine(buf->data, length);
    }
    return buf;
}

void destroy_window(lpbuffer_t* buf) {
    LPBuffer.destroy(buf);
}

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
lpfloat_t lpzapgremlins(lpfloat_t x) {
    lpfloat_t absx;
    absx = fabs(x);
    return (absx > (lpfloat_t)1e-15 && absx < (lpfloat_t)1e15) ? x : (lpfloat_t)0.f;
}

lpfloat_t lpfilternan(lpfloat_t x) {
    return isnan(x) ? 0.f : x;
}

lpfloat_t lpwv(lpfloat_t value, lpfloat_t min, lpfloat_t max) {
    /* wrap value */
    if(value > max) value -= max;
    if(value < min) value += min;
    return value;
}

lpfloat_t lpsv(lpfloat_t value, lpfloat_t min, lpfloat_t max) {
    /* scale value (for inputs 0-1) */
    return value * (max-min) + min;
}

lpfloat_t lpsvf(lpfloat_t value, lpfloat_t min, lpfloat_t max, lpfloat_t from, lpfloat_t to) {
    /* scale value from (a range other than 0-1) */
    lpfloat_t delta = to - from;
    if(delta <= 0) return 0;
    return (value/delta) * (max-min) + min;
}

lpfloat_t lpfmax(lpfloat_t a, lpfloat_t b) {
    if(isnan(a)) return b;
    if(isnan(b)) return a;
    return a < b ? b : a;
}

lpfloat_t lpfmin(lpfloat_t a, lpfloat_t b) {
    if (isnan(a)) return b;
    if (isnan(b)) return a;
    return a < b ? a : b;
}

lpfloat_t lpfabs(lpfloat_t value) {
    if(value <= 0) return value * -1;
    return value;
}

lpfloat_t lpfpow(lpfloat_t value, int exp) {
    int i;
    lpfloat_t result;

#if DEBUG
    assert(exp >= 0);
#endif

    result = 1.f;
    for(i=0; i < exp; i++) {
        result *= value;
    }
    return result;
}

lpfloat_t lpmstofreq(lpfloat_t ms) {
    return 1.f / (ms * 0.001f);
}

lpfloat_t lpstofreq(lpfloat_t seconds) {
    return 1.f / seconds;
}

/* FNV-1 hash implementation adapted from:
 * http://www.isthe.com/chongo/src/fnv/hash_32.c */
uint32_t lphashstr(char * str) {
    uint32_t hval = FNV1_32_MAGIC_NUMBER;
    unsigned char *s = (unsigned char *)str;	/* unsigned string */

    /* FNV-1 hash each octet in the buffer */
    while (*s) {
        /* multiply by the 32 bit FNV magic prime mod 2^32 */
        hval += (hval<<1) + (hval<<4) + (hval<<7) + (hval<<8) + (hval<<24);

        /* xor the bottom with the current octet */
        hval ^= (uint32_t)*s++;
    }

    /* return our new hash value */
    return hval;
}
