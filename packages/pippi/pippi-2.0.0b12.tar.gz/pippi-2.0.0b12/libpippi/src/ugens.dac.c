#include "ugens.dac.h"

lpfloat_t lpugen_dac_process(ugen_t * u) {
    if (u == NULL || u->type != UGEN_DAC) return 0.0f;

    // Get current parameter values
    lpfloat_t input = lpugen_get_param(u, UPARAM_INPUT);
    lpfloat_t gain = lpugen_get_param(u, UPARAM_GAIN);
    lpfloat_t channel = lpugen_get_param(u, UPARAM_CHANNEL);

    // Update channel in params struct for routing
    u->params.dac.channel = (int)channel;

    // Apply gain to input signal
    lpfloat_t output = input * gain;

    // Store for output retrieval
    u->params.dac.input_sample = output;

    // Update additional outputs
    u->outputs[0] = output;                           // Output signal
    u->outputs[1] = gain;                             // Current gain
    u->outputs[2] = channel;                          // Channel number

    return output;
}

lpfloat_t lpugen_dac_get_output_sample(ugen_t * u, int channel) {
    if (u != NULL && u->type == UGEN_DAC && u->params.dac.channel == channel) {
        return u->params.dac.input_sample;
    }
    return 0.0f;
}