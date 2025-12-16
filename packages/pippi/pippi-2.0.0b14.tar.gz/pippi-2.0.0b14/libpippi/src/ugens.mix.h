#ifndef LP_UGEN_MIX_H
#define LP_UGEN_MIX_H

#include "ugens.core.h"
#include <syslog.h>  // TODO: REMOVE - temporary for debugging

lpfloat_t lpugen_mix_process(ugen_t * u);
void lpugen_mix_set_input_sample(ugen_t * u, lpfloat_t sample);

#endif
