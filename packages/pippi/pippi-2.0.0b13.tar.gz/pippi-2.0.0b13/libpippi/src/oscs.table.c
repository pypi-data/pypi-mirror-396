#include "oscs.table.h"

// FIXME -- maybe this should be called oscs.lfo?

lptableosc_t * create_tableosc(lpbuffer_t * buf);
lpfloat_t process_tableosc(lptableosc_t * osc);
lpbuffer_t * render_tableosc(lptableosc_t * osc, size_t length, lpbuffer_t * amp, int channels);
void destroy_tableosc(lptableosc_t * osc);

const lptableosc_factory_t LPTableOsc = { create_tableosc, process_tableosc, render_tableosc, destroy_tableosc };

lptableosc_t * create_tableosc(lpbuffer_t * buf) {
    lptableosc_t* osc = (lptableosc_t*)LPMemoryPool.alloc(1, sizeof(lptableosc_t));
    osc->buf = buf;
    osc->samplerate = buf->samplerate;
    osc->gate = 0;
    osc->phase = 0.f;
    osc->pulsewidth = 1.f;
    osc->phaseinc = (lpfloat_t)buf->length / (lpfloat_t)buf->samplerate;
    osc->freq = 110.f;

    return osc;
}

lpfloat_t process_tableosc(lptableosc_t * osc) {
    int c;
    lpfloat_t f, a, b, sample=0, ipw=1;
    size_t idxa, idxb;

    if(osc->pulsewidth > 0) {
        ipw = 1.f/osc->pulsewidth;

        f = osc->phase - (int)osc->phase;
        idxa = (size_t)osc->phase;
        idxb = idxa + 1;

        sample = 0.f;

        for(c=0; c < osc->buf->channels; c++) {
            a = osc->buf->data[idxa * osc->buf->channels + c];
            b = osc->buf->data[idxb * osc->buf->channels + c];
            sample += (1.f - f) * a + (f * b);
        }
    }

    osc->phase += osc->phaseinc * osc->freq * ipw;

    if(osc->phase > osc->buf->length-1) {
        osc->phase -= osc->buf->length;
        osc->gate = 1;
    } else {
        osc->gate = 0;
    }

    return sample;
}

lpbuffer_t * render_tableosc(lptableosc_t * osc, size_t length, lpbuffer_t * amp, int channels) {
    lpbuffer_t * out;
    lpfloat_t _amp, sample;
    size_t i;
    int c;
    float pos;

    pos = 0.f;
    out = LPBuffer.create(length, channels, osc->samplerate);
    for(i=0; i < length; i++) {
        pos = (float)i/length;
        _amp = LPInterpolation.linear_pos(amp, pos);
        sample = process_tableosc(osc);
        for(c=0; c < channels; c++) {
            out->data[i * channels + c] = sample * _amp;
        }
    }

    return out;
}

void destroy_tableosc(lptableosc_t * osc) {
    LPMemoryPool.free(osc);
}


