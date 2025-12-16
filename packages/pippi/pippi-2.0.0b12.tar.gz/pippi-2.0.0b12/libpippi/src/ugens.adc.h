#ifndef LP_UGEN_ADC_H
#define LP_UGEN_ADC_H

#include "ugens.core.h"

// ADC ugen process function (called by core)
lpfloat_t lpugen_adc_process(ugen_t * u);

// ADC-specific helper functions for Jack integration
void lpugen_adc_set_input_sample(ugen_t * u, lpfloat_t sample);
lpfloat_t lpugen_adc_get_level(ugen_t * u);
lpfloat_t lpugen_adc_get_peak(ugen_t * u);

#endif