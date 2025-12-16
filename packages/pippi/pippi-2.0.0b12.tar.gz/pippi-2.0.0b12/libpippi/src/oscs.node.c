#include "oscs.node.h"

lpnode_t * lpnode_create(int node_type);
void lpnode_connect(lpnode_t * node, int param_type, lpnode_t * param, lpfloat_t minval, lpfloat_t maxval);
void lpnode_connect_signal(lpnode_t * node, int param_type, lpfloat_t value);
lpfloat_t lpnode_process(lpnode_t * node);
void lpnode_destroy(lpnode_t * node);

const lpnode_factory_t LPNode = { lpnode_create, lpnode_connect, lpnode_connect_signal, lpnode_process, lpnode_destroy };

lpnode_t * lpnode_create(int node_type) {
    lpnode_t * node;

    // create the node struct
    node = (lpnode_t *)LPMemoryPool.alloc(1, sizeof(lpnode_t));
    node->type = node_type;
    node->last = 0.f;

    // create the param struct in the appropriate flavor
    if(node_type == NODE_SIGNAL) {
        node->params.signal = (lpnode_signal_t *)LPMemoryPool.alloc(1, sizeof(lpnode_signal_t));
    } else if(node_type == NODE_SINEOSC) {
        node->params.sineosc = (lpnode_sineosc_t *)LPMemoryPool.alloc(1, sizeof(lpnode_sineosc_t));
        node->params.sineosc->freq_mul = 1.f;
        node->params.sineosc->freq_add = 0.f;
        node->params.sineosc->phase = 0.f;
        node->params.sineosc->samplerate = DEFAULT_SAMPLERATE;
    } else if(node_type == NODE_ADC) {
        node->params.adc = (lpnode_adc_t *)LPMemoryPool.alloc(1, sizeof(lpnode_adc_t));
        node->params.adc->gain_mul = 1.f;
        node->params.adc->gain_add = 0.f;
        node->params.adc->channel = 0;
        node->params.adc->current_sample = 0.f;
        node->params.adc->level_accumulator = 0.f;
        node->params.adc->peak_level = 0.f;
        node->params.adc->smoothing_factor = 0.1f;
        node->params.adc->level_output = 0.f;
        node->params.adc->peak_output = 0.f;
    }

    return node;
}

void lpnode_connect(lpnode_t * node, int param_type, lpnode_t * param, lpfloat_t minval, lpfloat_t maxval) {
    if(node->type == NODE_SINEOSC) {
        if(param_type == NODE_PARAM_FREQ) {
            node->params.sineosc->freq = param;
            node->params.sineosc->freq_mul = (maxval - minval) / 2.f;
            node->params.sineosc->freq_add = minval + node->params.sineosc->freq_mul;
        }
    } else if(node->type == NODE_ADC) {
        if(param_type == NODE_PARAM_GAIN) {
            node->params.adc->gain = param;
            node->params.adc->gain_mul = (maxval - minval) / 2.f;
            node->params.adc->gain_add = minval + node->params.adc->gain_mul;
        }
    }
}

void lpnode_connect_signal(lpnode_t * node, int param_type, lpfloat_t value) {
    if(node->type == NODE_SINEOSC) {
        if(param_type == NODE_PARAM_FREQ) {
            node->params.sineosc->freq = lpnode_create(NODE_SIGNAL);
            node->params.sineosc->freq->last = value;
            node->params.sineosc->freq->params.signal->value = value;
            node->params.sineosc->freq_mul = 1.f;
            node->params.sineosc->freq_add = 0.f;
        }
    } else if(node->type == NODE_ADC) {
        if(param_type == NODE_PARAM_GAIN) {
            node->params.adc->gain = lpnode_create(NODE_SIGNAL);
            node->params.adc->gain->last = value;
            node->params.adc->gain->params.signal->value = value;
            node->params.adc->gain_mul = 1.f;
            node->params.adc->gain_add = 0.f;
        } else if(param_type == NODE_PARAM_CHANNEL) {
            node->params.adc->channel = (int)value;
        }
    }
}


lpfloat_t lpnode_sineosc_process(lpnode_t * node) {
    lpfloat_t sample, freq;
    
    sample = sin((lpfloat_t)PI2 * node->params.sineosc->phase);
    freq = node->params.sineosc->freq->last;
    freq *= node->params.sineosc->freq_mul;
    freq += node->params.sineosc->freq_add;
    node->params.sineosc->phase += freq * (1.0f/node->params.sineosc->samplerate);

    while(node->params.sineosc->phase >= 1) {
        node->params.sineosc->phase -= 1.0f;
    }

    node->last = sample;
    return sample;
}

lpfloat_t lpnode_adc_process(lpnode_t * node) {
    lpfloat_t sample, gain, abs_sample;
    
    // Get gain (could be modulated by another node)
    gain = 1.0f;
    if(node->params.adc->gain != NULL) {
        gain = node->params.adc->gain->last;
        gain *= node->params.adc->gain_mul;
        gain += node->params.adc->gain_add;
    }
    
    // Apply gain to current input sample
    sample = node->params.adc->current_sample * gain;
    
    // Update level smoothing
    abs_sample = fabs(sample);
    node->params.adc->level_accumulator = 
        (node->params.adc->level_accumulator * (1.0f - node->params.adc->smoothing_factor)) +
        (abs_sample * node->params.adc->smoothing_factor);
    node->params.adc->level_output = node->params.adc->level_accumulator;
    
    // Update peak detection with decay
    if(abs_sample > node->params.adc->peak_level) {
        node->params.adc->peak_level = abs_sample;
    } else {
        node->params.adc->peak_level *= 0.9999f;
    }
    node->params.adc->peak_output = node->params.adc->peak_level;
    
    node->last = sample;
    return sample;
}

lpfloat_t lpnode_process(lpnode_t * node) {
    if(node->type == NODE_SIGNAL) {
        return node->params.signal->value;
    } else if(node->type == NODE_SINEOSC) {
        return lpnode_sineosc_process(node);        
    } else if(node->type == NODE_ADC) {
        return lpnode_adc_process(node);
    }

    return 0;
}

void lpnode_destroy(lpnode_t * node) {
    LPMemoryPool.free(node);
}

// ADC-specific helper functions
void lpnode_adc_set_input_sample(lpnode_t * adc_node, lpfloat_t sample) {
    if(adc_node != NULL && adc_node->type == NODE_ADC) {
        adc_node->params.adc->current_sample = sample;
    }
}

lpfloat_t lpnode_adc_get_level(lpnode_t * adc_node) {
    if(adc_node != NULL && adc_node->type == NODE_ADC) {
        return adc_node->params.adc->level_output;
    }
    return 0.0f;
}

lpfloat_t lpnode_adc_get_peak(lpnode_t * adc_node) {
    if(adc_node != NULL && adc_node->type == NODE_ADC) {
        return adc_node->params.adc->peak_output;
    }
    return 0.0f;
}
