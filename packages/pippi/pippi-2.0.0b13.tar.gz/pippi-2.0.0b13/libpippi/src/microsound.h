#ifndef LP_GRAINS_H
#define LP_GRAINS_H

#include "pippicore.h"
#include "oscs.tape.h"
#include "oscs.table.h"

#define LPFORMATION_MAXGRAINS 64

typedef struct lpgrain_t {
    size_t length;
    int channels;
    lpfloat_t samplerate; 
    lpfloat_t pulsewidth; 
    lpfloat_t grainlength;
    size_t offset; /* from start of src buffer in frames */

    lpfloat_t pan;
    lpfloat_t amp;
    lpfloat_t speed;
    lpfloat_t skew; /* phase distortion on the grain window */

    int gate;
    int active; /* when 1, this grain is engaged in playback
                   when 0, this grain has stopped and needs to 
                   be reset again to resume playback. 

                   reset means phase set to zero,
                   and active is set to 1
                */

    lptapeosc_t * src;
    lptableosc_t * win;
} lpgrain_t;

typedef struct lpformation_t {
    lpgrain_t grains[LPFORMATION_MAXGRAINS];
    lpgrain_t * active_grains[LPFORMATION_MAXGRAINS];
    lpfloat_t grainlength;
    lpfloat_t grainlength_maxjitter;
    lpfloat_t grainlength_jitter; /* 0-1 proportional to grainlength_maxjitter */
    lpfloat_t grid_maxjitter;
    lpfloat_t grid_jitter;

    int num_total_grains;  /* total number of used grains between 1 and MAXGRAINS */
    int num_active_grains; /* number of active grains */

    lpfloat_t spread; /* pan spread */
    lpfloat_t speed;
    lpfloat_t length; /* length of the src buffer in seconds copied from source on init */
    size_t offset; /* from src buffer in frames */
    lpfloat_t interval; /* in seconds */
    lpfloat_t phaseinc; /* 1/interval for phase inc */
    lpfloat_t phase; /* 0-1 as the position in the offset */
    int gate; /* high on gate / offset reset */
    lpfloat_t skew;
    lpfloat_t amp;
    lpfloat_t pan;
    lpfloat_t pulsewidth; 

    lpbuffer_t * source;
    lpbuffer_t * window;
    lpbuffer_t * current_frame;
} lpformation_t;

typedef struct lpformation_factory_t {
    lpformation_t * (*create)(lpbuffer_t * src, lpbuffer_t * win);
    void (*init)(lpformation_t *); /* activates the initial grain -- allows metadata update after create */
    void (*update_interval)(lpformation_t *, lpfloat_t new_interval);
    void (*increment_offset)(lpformation_t *);
    void (*process)(lpformation_t *);
    void (*destroy)(lpformation_t *);
} lpformation_factory_t;

void grain_init(lpgrain_t * grain, lpbuffer_t * src, lpbuffer_t * win);
void grain_process(lpgrain_t * g, lpbuffer_t * out);

extern const lpformation_factory_t LPFormation;

#endif
