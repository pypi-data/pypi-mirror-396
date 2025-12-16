#ifndef LP_PULSAR_H
#define LP_PULSAR_H

#include "pippicore.h"
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>

#define MAX_PULSAR_WAVETABLES 4096
#define MAX_PULSAR_WINDOWS 4096
#define MAX_PULSAR_BURST 4096

typedef struct lppulsarosc_t {
    lpbuffer_t * wavetables[MAX_PULSAR_WAVETABLES];   /* Wavetable stack */
    int num_wavetables;
    lpfloat_t wavetable_morph;
    lpfloat_t wavetable_morph_freq;

    lpbuffer_t * windows[MAX_PULSAR_WINDOWS];  /* Window stack */
    int num_windows;
    lpfloat_t window_morph;
    lpfloat_t window_morph_freq;

    bool burst[MAX_PULSAR_BURST];         /* Burst table - null table == pulses always on */
    bool saturation_toggle; /* On pulse edges calculate this boolean which may
                               override the burst table */
    size_t burst_size;
    size_t burst_pos; 

    bool once;  /* if once is true, after the phase overflows the osc returns zeros
                   instead of resetting the phase to 0, to use the osc as a one-shot... */
    bool pulse_edge;
    lpfloat_t phase;
    lpfloat_t saturation; /* Probability of all pulses to no pulses */
    lpfloat_t pulsewidth;
    lpfloat_t samplerate;
    lpfloat_t freq;
} lppulsarosc_t;

typedef struct lppulsarosc_factory_t {
    lppulsarosc_t * (*create)();
    int (*add_wavetable)(lppulsarosc_t * osc, lpbuffer_t * wt);
    int (*add_window)(lppulsarosc_t * osc, lpbuffer_t * win);
    void (*burst_file)(lppulsarosc_t * osc, char * filename, size_t burst_size);
    void (*burst_bytes)(lppulsarosc_t * osc, unsigned char * bytes, size_t burst_size);
    lpfloat_t (*process)(lppulsarosc_t *);
    void (*destroy)(lppulsarosc_t*);
} lppulsarosc_factory_t;

extern const lppulsarosc_factory_t LPPulsarOsc;

#endif
