#include "ugens.mix.h"

lpfloat_t lpugen_mix_process(ugen_t * u) {
    if (u == NULL || u->type != UGEN_MIX) return 0.0f;

    // Get current parameter values
    lpfloat_t gain = lpugen_get_param(u, UPARAM_GAIN);
    lpfloat_t channel = lpugen_get_param(u, UPARAM_CHANNEL);

    // Update channel in params struct for routing
    u->params.mix.channel = (int)channel;

    // Apply gain to current sample (already set by stream callback)
    lpfloat_t output = u->params.mix.current_sample * gain;

    // Update additional outputs
    u->outputs[0] = output;                           // Output signal
    u->outputs[1] = gain;                             // Current gain
    u->outputs[2] = channel;                          // Channel number

    return output;
}

void lpugen_mix_set_input_sample(ugen_t * u, lpfloat_t sample) {
    if (u != NULL && u->type == UGEN_MIX) {
        u->params.mix.current_sample = sample;
    }
}
