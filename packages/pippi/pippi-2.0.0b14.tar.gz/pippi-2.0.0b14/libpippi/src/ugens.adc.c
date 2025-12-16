#include "ugens.adc.h"

lpfloat_t lpugen_adc_process(ugen_t * u) {
    if (u == NULL || u->type != UGEN_ADC) return 0.0f;

    // Get current parameter values
    lpfloat_t gain = lpugen_get_param(u, UPARAM_GAIN);
    lpfloat_t channel = lpugen_get_param(u, UPARAM_CHANNEL);

    // Update channel in params struct for routing
    u->params.adc.channel = (int)channel;

    // Apply gain to current input sample
    lpfloat_t sample = u->params.adc.current_sample * gain;
    
    // Update level smoothing
    lpfloat_t abs_sample = fabs(sample);
    u->params.adc.level_accumulator = 
        (u->params.adc.level_accumulator * (1.0f - u->params.adc.smoothing_factor)) +
        (abs_sample * u->params.adc.smoothing_factor);
    
    // Update peak detection with decay
    if (abs_sample > u->params.adc.peak_level) {
        u->params.adc.peak_level = abs_sample;
    } else {
        u->params.adc.peak_level *= 0.9999f;
    }
    
    // Update additional outputs
    u->outputs[0] = u->params.adc.level_accumulator;  // Smoothed level
    u->outputs[1] = u->params.adc.peak_level;         // Peak level
    u->outputs[2] = gain;                             // Current gain
    u->outputs[3] = channel;                          // Channel number

    return sample;
}

void lpugen_adc_set_input_sample(ugen_t * u, lpfloat_t sample) {
    if (u != NULL && u->type == UGEN_ADC) {
        u->params.adc.current_sample = sample;
    }
}

lpfloat_t lpugen_adc_get_level(ugen_t * u) {
    if (u != NULL && u->type == UGEN_ADC) {
        return u->outputs[0];  // Level is first additional output
    }
    return 0.0f;
}

lpfloat_t lpugen_adc_get_peak(ugen_t * u) {
    if (u != NULL && u->type == UGEN_ADC) {
        return u->outputs[1];  // Peak is second additional output
    }
    return 0.0f;
}