#ifndef LP_NODEOSC_H
#define LP_NODEOSC_H

#include "pippicore.h"

typedef struct lpnode_t lpnode_t;

enum NodeTypes {
    NODE_TABLE,
    NODE_SIGNAL,
    NODE_SINEOSC,
    NODE_ADC
};

enum ParamTypes {
    NODE_PARAM_FREQ,
    NODE_PARAM_AMP,
    NODE_PARAM_GAIN,
    NODE_PARAM_CHANNEL
};

typedef struct lpnode_table_t {
    lpbuffer_t * buf;
    lpfloat_t * freq;
} lpnode_table_t;

typedef struct lpnode_signal_t {
    lpfloat_t value;
} lpnode_signal_t;

typedef struct lpnode_sineosc_t {
    lpnode_t * freq;
    lpfloat_t freq_mul;
    lpfloat_t freq_add;
    lpfloat_t phase;
    lpfloat_t samplerate;
} lpnode_sineosc_t;

typedef struct lpnode_adc_t {
    lpnode_t * gain;
    lpfloat_t gain_mul;
    lpfloat_t gain_add;
    int channel;
    lpfloat_t current_sample;      // Current input sample from Jack
    lpfloat_t level_accumulator;   // For level smoothing
    lpfloat_t peak_level;         // Peak detection
    lpfloat_t smoothing_factor;   // Level smoothing amount
    lpfloat_t level_output;       // Smoothed level output
    lpfloat_t peak_output;        // Peak level output
} lpnode_adc_t;

typedef struct lpnode_t {
    int type;
    lpfloat_t last;
    union params {
        lpnode_table_t * table;
        lpnode_signal_t * signal;
        lpnode_sineosc_t * sineosc;
        lpnode_adc_t * adc;
    } params;
} lpnode_t;

typedef struct lpnode_factory_t {
    lpnode_t * (*create)(int node_type);
    void (*connect)(lpnode_t * node, int param_type, lpnode_t * param, lpfloat_t minval, lpfloat_t maxval);
    void (*connect_signal)(lpnode_t * node, int param_type, lpfloat_t value);
    lpfloat_t (*process)(lpnode_t * node);
    void (*destroy)(lpnode_t * node);
} lpnode_factory_t;

extern const lpnode_factory_t LPNode;

// ADC-specific functions for feeding Jack input
void lpnode_adc_set_input_sample(lpnode_t * adc_node, lpfloat_t sample);
lpfloat_t lpnode_adc_get_level(lpnode_t * adc_node);
lpfloat_t lpnode_adc_get_peak(lpnode_t * adc_node);

#endif
