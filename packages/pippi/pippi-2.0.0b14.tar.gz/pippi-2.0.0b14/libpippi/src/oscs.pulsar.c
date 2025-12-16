#include "oscs.pulsar.h"

void burst_table_from_bytes(lppulsarosc_t * osc, unsigned char * bytes, size_t burst_size) {
    int mask;
    size_t i, c, pos;
    size_t num_bytes = (burst_size + sizeof(unsigned char) - 1) / sizeof(unsigned char);

    memset(osc->burst, 0, sizeof(osc->burst));

    pos = 0;
    for(i=0; i < num_bytes; i++) {
        for(c=0; c < sizeof(unsigned char); c++) {
            if(pos >= burst_size) break;
            mask = 1 << c;
            osc->burst[pos] = (bool)((bytes[i] & mask) >> c);
            pos += 1;
        }
    }

    osc->burst_size = burst_size;
}

void burst_table_from_file(lppulsarosc_t * osc, char * filename, size_t burst_size) {
    int fp;
    size_t num_bytes = (burst_size + sizeof(unsigned char) - 1) / sizeof(unsigned char);
    unsigned char burst_buffer[num_bytes];

    memset(burst_buffer, 0, num_bytes * sizeof(unsigned char));

    fp = open(filename, O_RDONLY);
    if(fp < 0) {
        close(fp);
        return;
    }

    if(read(fp, burst_buffer, num_bytes) < 0) {
        close(fp);
        return;
    }

    close(fp);

    burst_table_from_bytes(osc, burst_buffer, burst_size);
}

int add_wavetable(lppulsarosc_t * p, lpbuffer_t * wt) {
    if(p->num_wavetables >= MAX_PULSAR_WAVETABLES) {
        return -1;
    }
    lpbuffer_t * buf = LPBuffer.clone(wt);
    p->wavetables[p->num_wavetables] = buf;
    p->num_wavetables += 1;
    return 0;
}

int add_window(lppulsarosc_t * p, lpbuffer_t * wt) {
    if(p->num_windows >= MAX_PULSAR_WAVETABLES) {
        return -1;
    }
    lpbuffer_t * buf = LPBuffer.clone(wt);
    p->windows[p->num_windows] = buf;
    p->num_windows += 1;
    return 0;
}

lppulsarosc_t * create_pulsarosc() {
    lppulsarosc_t * p = (lppulsarosc_t *)LPMemoryPool.alloc(1, sizeof(lppulsarosc_t));
    memset(p, 0, sizeof(lppulsarosc_t));

    p->wavetable_morph_freq = 1.f;
    p->window_morph_freq = 1.f;
    p->saturation_toggle = 1;
    p->saturation = 1.f;
    p->pulsewidth = 1.f;
    p->samplerate = DEFAULT_SAMPLERATE;
    p->freq = 220.0;

    return p;
}

lpfloat_t process_pulsarosc(lppulsarosc_t * p) {
    lpfloat_t ipw, isr, sample, a, b, 
              wtmorphpos, wtmorphfrac,
              winmorphpos, winmorphfrac;
    int wavetable_index, window_index;
    int burst;

    assert(p->samplerate > 0);
    wavetable_index = 0;
    window_index = 0;
    isr = 1.f / (lpfloat_t)p->samplerate;
    ipw = 0.f;
    sample = 0.f;
    burst = 1;

    /* Store the inverse pulsewidth if non-zero */
    if(p->pulsewidth > 0) ipw = 1.0/p->pulsewidth;

    /* Look up the burst value -- NULL burst is always on. 
     * In other words, bursting only happens when the burst 
     * table is non-NULL. Otherwise all pulses sound. */
    if(p->burst_size > 0) burst = p->burst[p->burst_pos % p->burst_size];
    if(!p->saturation_toggle) burst = 0;

    /* Treat the pulse as a one-shot. Reset the phase to rewind, or toggle once off */
    if(p->phase >= 1.f && p->once) return 0.f;

    /* If there's a non-zero pulsewidth, and the burst value is 1, 
     * then syntesize a pulse */
    if(p->pulsewidth > 0 && burst && p->phase < p->pulsewidth) {
        wtmorphpos = p->wavetable_morph * (p->num_wavetables-1);
        wavetable_index = (int)wtmorphpos;
        winmorphpos = p->window_morph * (p->num_windows-1);
        window_index = (int)winmorphpos;

        sample = 1.f; // When num_wavetables == 0, the window functions can be used like an LFO
        if(p->num_wavetables <= 1) {
            sample = LPInterpolation.linear_pos(p->wavetables[wavetable_index], p->phase * ipw);
        } else if(p->num_wavetables > 0) {
            wtmorphfrac = wtmorphpos - wavetable_index;

            a = LPInterpolation.linear_pos(p->wavetables[wavetable_index], p->phase * ipw);
            b = LPInterpolation.linear_pos(p->wavetables[wavetable_index+1], p->phase * ipw);

            sample = (1.f - wtmorphfrac) * a + (wtmorphfrac * b);
        }

        // When num_windows == 0, this is a noop
        if(p->num_windows <= 1) {
            sample *= LPInterpolation.linear_pos(p->windows[window_index], p->phase * ipw);
        } else if(p->num_windows > 0) {
            winmorphfrac = winmorphpos - window_index;
           
            a = LPInterpolation.linear_pos(p->windows[window_index], p->phase * ipw);
            b = LPInterpolation.linear_pos(p->windows[window_index+1], p->phase * ipw);

            sample *= (1.f - winmorphfrac) * a + (winmorphfrac * b);
        }
    } 

    // increment phases
    p->wavetable_morph += isr * p->wavetable_morph_freq;
    p->window_morph += isr * p->window_morph_freq;
    //p->phase += isr * p->freq / (p->pulsewidth > 0 ? p->pulsewidth : 1.f);
    p->phase += isr * p->freq;

    if(p->phase >= 1.f) p->burst_pos += 1;

    // Set the pulse boundary flag so external programs can know
    // about phase boundries (and do things when they happen)
    p->pulse_edge = (p->phase >= 1.f);

    /* Override burst on pulse edges if desaturation is triggered */
    if(p->pulse_edge) {
        if(p->saturation < 1.f && LPRand.rand(0.f, 1.f) > p->saturation) {
            p->saturation_toggle = 0;
        } else {
            p->saturation_toggle = 1;
        }
    }

    // wrap phases unless once is toggled
    if(p->once) return sample;
    if(p->phase < 0) {
        while(p->phase < 0) p->phase += 1.f;
    } else if(p->phase >= 1.f) {
        while(p->phase >= 1.f) p->phase -= 1.f;
    }

    while(p->wavetable_morph >= 1.f) p->wavetable_morph -= 1.f;
    while(p->window_morph >= 1.f) p->window_morph -= 1.f;
    if(p->burst_size > 0) while(p->burst_pos >= p->burst_size) p->burst_pos -= p->burst_size;

    return sample;
}

void destroy_pulsarosc(lppulsarosc_t* p) {
    for(int i=0; i < p->num_wavetables; i++) {
        LPBuffer.destroy(p->wavetables[i]);
    }
    for(int i=0; i < p->num_windows; i++) {
        LPBuffer.destroy(p->windows[i]);
    }
    LPMemoryPool.free(p);
}

const lppulsarosc_factory_t LPPulsarOsc = { 
    create_pulsarosc, 
    add_wavetable,
    add_window,
    burst_table_from_file, 
    burst_table_from_bytes, 
    process_pulsarosc, 
    destroy_pulsarosc 
};
