#include "ugens.sine.h"

lpfloat_t lpugen_sine_process(ugen_t * u) {
    if (u == NULL || u->type != UGEN_SINE) return 0.0f;
    
    // Get current parameter values (could be from connections or direct values)
    lpfloat_t freq = lpugen_get_param(u, UPARAM_FREQ);
    lpfloat_t phase_offset = lpugen_get_param(u, UPARAM_PHASE);
    
    // Update the internal sine parameters
    u->params.sine.phase += freq / u->params.sine.samplerate;
    
    // Wrap phase
    while (u->params.sine.phase >= 1.0f) {
        u->params.sine.phase -= 1.0f;
    }
    while (u->params.sine.phase < 0.0f) {
        u->params.sine.phase += 1.0f;
    }
    
    // Calculate sine output with phase offset
    lpfloat_t total_phase = u->params.sine.phase + phase_offset;
    lpfloat_t output = sin(PI2 * total_phase);
    
    // Update additional outputs
    u->outputs[0] = freq;               // Current frequency
    u->outputs[1] = u->params.sine.phase; // Current phase
    
    return output;
}

