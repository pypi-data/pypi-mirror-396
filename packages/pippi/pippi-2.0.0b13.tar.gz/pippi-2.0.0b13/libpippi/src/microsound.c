#include "microsound.h"

#ifndef DEBUG
#define DEBUG 0
#endif
#if DEBUG
#include <errno.h>
#endif


void grain_process(lpgrain_t * g, lpbuffer_t * out) {
    int c, oc=0;
    lpfloat_t win=0.f;

#if DEBUG
    assert(!isnan(g->src->phase));
    assert(g->samplerate > 0);
    assert(g->grainlength > 0);
    assert(out->length == 1); // outbuf is just a single frame vector
#endif

    if(g->pulsewidth <= 0) return;

    LPTapeOsc.process(g->src); 
    win = LPTableOsc.process(g->win); 

    g->gate = g->src->gate;
    /* if we've hit a phase boundary, set the grain 
     * to inactive to signal that it can be reused */
    if(g->gate) g->active = 0;

    /* grain sources get mapped to the grain output channels */
    for(c=0; c < out->channels; c++) {
        oc = c; 
        while(oc >= g->src->current_frame->channels) oc -= g->src->current_frame->channels;
        out->data[c] += g->src->current_frame->data[oc] * win;
    }
}

void grain_init(lpgrain_t * grain, lpbuffer_t * src, lpbuffer_t * win) {
    win->samplerate = src->samplerate;
    grain->src = LPTapeOsc.create(src);
    grain->win = LPTableOsc.create(win);
    grain->offset = 0;
    grain->channels = src->channels;
    grain->samplerate = src->samplerate;
    grain->pulsewidth = 1.f;
}

void formation_grain_reset(lpformation_t * f, lpgrain_t * g) {
    g->pulsewidth = f->pulsewidth;
    g->speed = f->speed;
    g->active = 1;
    g->src->phase = 0.f;
    g->win->phase = 0.f;

    if(f->spread > 0) {
        g->pan = .5f + LPRand.rand(-.5f, .5f) * f->spread;
    } else {
        g->pan = f->pan;
    }

    if(f->grainlength_jitter > 0) {
        g->grainlength = f->grainlength + (size_t)LPRand.rand(0, f->grainlength_jitter * f->grainlength_maxjitter);
    } else {
        g->grainlength = f->grainlength;
    }

    if(f->grid_jitter > 0) {
        g->offset = f->offset + (size_t)LPRand.rand(0, f->grid_jitter * f->grid_maxjitter);
    } else {
        g->offset = f->offset;
    }

    g->win->freq = g->speed * (1.f / (lpfloat_t)g->grainlength);
    g->src->range = g->grainlength * g->samplerate;
    g->src->start = g->offset;
    g->src->speed = g->speed;
    g->win->pulsewidth = g->pulsewidth;

    if(f->num_active_grains < f->num_total_grains-1) {
        f->active_grains[f->num_active_grains] = g;
        f->num_active_grains += 1;
    /*} else {
        printf("no more grains available! dropping this one...\n");*/
    }
}

void formation_update_interval(lpformation_t * f, lpfloat_t new_interval) {
    if(new_interval <= 0) return;
;
    f->interval = new_interval;
    f->phaseinc = (1.f/(lpfloat_t)(f->source->samplerate * f->interval * (1./f->speed)));
}

lpformation_t * formation_create(lpbuffer_t * src, lpbuffer_t * win) {
    lpformation_t * f;
    int g;

#if DEBUG
    assert(src->samplerate > 0);
    assert(src->length > 0);
    assert(src->channels > 0);
#endif

    f = (lpformation_t *)LPMemoryPool.alloc(1, sizeof(lpformation_t));
    f->current_frame = LPBuffer.create(1, src->channels, src->samplerate);
    f->num_total_grains = 32;
    f->num_active_grains = 0;
    f->grainlength = 0.2f;
    f->pulsewidth = 1.f;
    f->offset = 0;
    f->speed = 1.f;
    f->pan = 0.5f;
    f->interval = 1.f;
    f->phaseinc = (1.f/(lpfloat_t)(src->samplerate * f->interval));
    f->length = src->length / (lpfloat_t)src->samplerate;

    f->source = src;
    f->window = win;

    for(g=0; g < f->num_total_grains; g++) {
        grain_init(&f->grains[g], src, win);
        f->grains[g].grainlength = f->grainlength;
        f->grains[g].offset = f->offset;
        f->grains[g].pulsewidth = f->pulsewidth;
        f->grains[g].pan = f->pan;
        f->grains[g].active = 0;
        f->grains[g].src->speed = f->speed;
        f->grains[g].win->phase = f->grains[g].src->phase;
    }

    return f;
}

void formation_init(lpformation_t * f) {
    // prime the formation with one active grain
    formation_grain_reset(f, &f->grains[0]);
}

void formation_increment_offset(lpformation_t * f) {
    if(f->source->length == 0) return; // Prevent infinite loop
    f->offset += f->interval * f->source->samplerate;
    while(f->offset >= f->source->length) {
        f->offset -= f->source->length;
    }
}

void formation_process(lpformation_t * f) {
    int i;

    memset(f->current_frame->data, 0, sizeof(lpfloat_t) * f->current_frame->channels);

    f->gate = 0; // set the grain activation gate low

    for(i=0; i < f->num_active_grains; i++) {
        if(f->active_grains[i]->active == 0) continue;

        grain_process(f->active_grains[i], f->current_frame);
        
        if(f->active_grains[i]->active == 0) {
            f->active_grains[i] = f->active_grains[f->num_active_grains-1];
            f->num_active_grains -= 1;
            i -= 1;
        }
    }

    f->phase += f->phaseinc;
    if (f->phase >= 1.f) {
        f->gate = 1; // indicate when a new grain is active
        //printf("phase reset interval=%f\n", f->interval);
        f->phase -= 1.f;
        // find an inactive grain and reset it
        for(i=0; i < f->num_total_grains; i++) {
            if(f->grains[i].active == 1) continue;
            // Sync formation parameters before resetting grain
            formation_grain_reset(f, &f->grains[i]);
            break;
        }
    }

    //if(isnan(f->phase) || isinf(f->phase)) f->phase = 0.f;
    while(f->phase > 1.f) f->phase -= 1.f;

}

void formation_destroy(lpformation_t * f) {
    LPBuffer.destroy(f->current_frame);
    for(int g=0; g < f->num_total_grains; g++) {
        LPTapeOsc.destroy(f->grains[g].src);
        LPTableOsc.destroy(f->grains[g].win);
    }
    LPMemoryPool.free(f);
}

/**
 * Waveset segmentation tools
 */
int extract_wavesets(
    int num_wavesets,
    int num_crossings,
    lpfloat_t * source_buffer, 
    size_t source_buffer_length, 
    lpfloat_t * waveset_buffer, 
    size_t waveset_buffer_length,
    size_t * waveset_onsets,
    size_t * waveset_lengths
) {
    size_t i, j, lastonset;
    int current, lastsign, crossing_count, waveset_count;
    lpfloat_t input;

    input = 0.f;
    lastsign = 0;
    lastonset = 0;
    crossing_count = 0;
    waveset_count = 0;
    j = 0;

    for(i=0; i < source_buffer_length; i++) {
        if(j >= waveset_buffer_length) break;
        if(waveset_count >= num_wavesets) break;

        input = source_buffer[i];

        current = signbit(input); 
        if((lastsign && !current) || (!lastsign && current)) {
            crossing_count += 1;

            if(crossing_count >= num_crossings) {
                waveset_lengths[waveset_count] = lastonset - j;
                waveset_onsets[waveset_count] = j;
                lastonset = j;

                waveset_count += 1;
                crossing_count = 0;
            }
        }

        lastsign = current;
        waveset_buffer[j] = input;

        j += 1;
    }

    return 0;
}

const lpformation_factory_t LPFormation = { 
    formation_create, 
    formation_init,
    formation_update_interval,
    formation_increment_offset,
    formation_process, 
    formation_destroy 
};
