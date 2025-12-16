#ifndef LP_UGEN_TAPE_H
#define LP_UGEN_TAPE_H

#include "ugens.core.h"
#include "oscs.tape.h"

#define UGEN_TAPE_PARAM_FREQ "freq"
#define UGEN_TAPE_PARAM_PHASE "phase"

enum UgenTapeParams {
    UTAPEIN_SPEED,
    UTAPEIN_PHASE,
    UTAPEIN_BUF,
    UTAPEIN_START,
    UTAPEIN_START_INCREMENT,
    UTAPEIN_RANGE,
};

enum UgenTapeOutputs {
    UTAPEOUT_MAIN,
    UTAPEOUT_SPEED,
    UTAPEOUT_PHASE,
    UTAPEOUT_GATE,
};

typedef struct lpugentape_t {
    lptapeosc_t * osc;
    lpfloat_t outputs[4];
} lpugentape_t;

// Legacy interface for Cython compatibility
ugen_t * create_tape_ugen(void);

// New unified interface
lpfloat_t lpugen_tape_process(ugen_t * u);

#endif
