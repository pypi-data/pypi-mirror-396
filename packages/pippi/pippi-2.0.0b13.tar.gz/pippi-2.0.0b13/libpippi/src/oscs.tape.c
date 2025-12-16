#include "oscs.tape.h"

#ifndef DEBUG
#define DEBUG 0
#endif
#if DEBUG
#include <errno.h>
#endif

lptapeosc_t * create_tapeosc(lpbuffer_t * buf);
void process_tapeosc(lptapeosc_t * osc);
void rewind_tapeosc(lptapeosc_t * osc);
lpbuffer_t * render_tapeosc(lptapeosc_t * osc, size_t length, lpbuffer_t * amp, int channels);
void destroy_tapeosc(lptapeosc_t * osc);

const lptapeosc_factory_t LPTapeOsc = { 
    create_tapeosc, 
    process_tapeosc, 
    rewind_tapeosc, 
    render_tapeosc, 
    destroy_tapeosc 
};

lptapeosc_t * create_tapeosc(lpbuffer_t * buf) {
#if DEBUG
    assert(buf != NULL);
    assert(buf->channels > 0);
    assert(buf->samplerate > 0);
#endif

    lptapeosc_t* osc = (lptapeosc_t*)LPMemoryPool.alloc(1, sizeof(lptapeosc_t));
    osc->buf = buf;

    osc->samplerate = buf->samplerate;
    osc->range = buf->length;
    osc->gate = 0;

    osc->phase = 0.f;
    osc->speed = 1.f;
    osc->start = 0.f;
    osc->current_frame = LPBuffer.create(1, buf->channels, buf->samplerate);
    return osc;
}

void rewind_tapeosc(lptapeosc_t * osc) {
    osc->start = 0;
    osc->phase = 0;
}

void process_tapeosc(lptapeosc_t * osc) {
    lpfloat_t sample, f, a, b, phase;
    int c, channels;
    size_t idxa, idxb;

#if DEBUG
    assert(osc->range != 0);
#endif

    channels = osc->buf->channels;

    phase = osc->phase * osc->range + osc->start;
    while(phase >= osc->buf->length-1) phase -= osc->buf->length-1;
    //while(phase >= osc->range-1) phase -= osc->range-1;

    f = phase - (int)phase;
    idxa = (size_t)phase;
    idxb = idxa + 1;

    for(c=0; c < channels; c++) {
        a = osc->buf->data[idxa * channels + c];
        b = osc->buf->data[idxb * channels + c];
        sample = (1.f - f) * a + (f * b);
        osc->current_frame->data[c] = sample;
    }

    osc->phase += osc->speed * (1.f/osc->range);

    if(osc->phase >= 1.f) {
        osc->gate = 1;
    } else {
        osc->gate = 0;
    }

    while(osc->phase >= 1.f) osc->phase -= 1.f;
}

lpbuffer_t * render_tapeosc(lptapeosc_t * osc, size_t length, lpbuffer_t * amp, int channels) {
    lpbuffer_t * out;
    lpfloat_t _amp;
    size_t i;
    int c;
    float pos;

    pos = 0.f;
    out = LPBuffer.create(length, channels, osc->samplerate);
    for(i=0; i < length; i++) {
        pos = (float)i/length;
        _amp = LPInterpolation.linear_pos(amp, pos);
        process_tapeosc(osc);
        for(c=0; c < channels; c++) {
            out->data[i * channels + c] = osc->current_frame->data[c] * _amp;
        }
    }

    return out;
}

void destroy_tapeosc(lptapeosc_t * osc) {
    LPBuffer.destroy(osc->current_frame);
    LPMemoryPool.free(osc);
}
