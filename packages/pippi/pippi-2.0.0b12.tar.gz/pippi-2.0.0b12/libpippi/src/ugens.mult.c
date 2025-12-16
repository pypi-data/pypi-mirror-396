#include "ugens.mult.h"

lpfloat_t lpugen_mult_process(ugen_t * u) {
    if (u == NULL || u->type != UGEN_MULT) return 0.0f;
    
    lpfloat_t a, b, result;
    
    // Update parameters from connections or direct values
    if (u->param_sources[UPARAM_A]) {
        a = u->param_sources[UPARAM_A]->output * u->param_mults[UPARAM_A] + u->param_adds[UPARAM_A];
    } else {
        a = u->param_values[UPARAM_A];
    }
    
    if (u->param_sources[UPARAM_B]) {
        b = u->param_sources[UPARAM_B]->output * u->param_mults[UPARAM_B] + u->param_adds[UPARAM_B];
    } else {
        b = u->param_values[UPARAM_B];
    }
    
    // Multiply the inputs
    result = a * b;
    
    // Set outputs
    u->output = result;
    u->outputs[0] = a;      // A output
    u->outputs[1] = b;      // B output
    u->num_outputs = 2;
    
    return result;
}