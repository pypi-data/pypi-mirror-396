#ifndef LP_UGEN_DAC_H
#define LP_UGEN_DAC_H

#include "ugens.core.h"

// DAC ugen process function (called by core)
lpfloat_t lpugen_dac_process(ugen_t * u);

// DAC-specific helper functions for Jack integration
lpfloat_t lpugen_dac_get_output_sample(ugen_t * u, int channel);

#endif