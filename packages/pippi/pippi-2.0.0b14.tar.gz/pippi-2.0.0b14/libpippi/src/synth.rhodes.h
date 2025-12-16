#ifndef LP_RHODESSYNTH_H
#define LP_RHODESSYNTH_H

#include "pippicore.h"
#include "oscs.bln.h"
#include "oscs.table.h"

#define NUM_PARTIALS 3
#define PARTIALS (lpfloat_t[]){1, 2, 3}

typedef struct lprhodesvoice_t {
    lptableosc_t oscs[NUM_PARTIALS];
    lptableosc_t env;
    lpblnosc_t noise;
    lpfloat_t freq;
    lpfloat_t pan;
} lprhodesvoice_t;

typedef struct lprhodessynth_t {
    lprhodesvoice_t ** voices;
    int numvoices;
    int channels;
    lpfloat_t samplerate;
} lprhodessynth_t;

typedef struct lprhodessynth_factory_t {
    lprhodessynth_t * (*create)(lpbuffer_t *, int, int);
    lpfloat_t (*process)(lprhodessynth_t *);
    lpbuffer_t * (*render)(lprhodessynth_t *, size_t, lpbuffer_t *, int);
    void (*destroy)(lprhodessynth_t *);
} lprhodessynth_factory_t;

extern const lprhodessynth_factory_t LPRhodesSynth;

#endif
