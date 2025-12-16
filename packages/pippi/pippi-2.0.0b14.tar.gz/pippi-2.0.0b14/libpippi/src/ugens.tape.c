#include "pippi.h"
#include "ugens.tape.h"
#include "oscs.tape.h"

// New unified interface implementation
lpfloat_t lpugen_tape_process(ugen_t * u) {
    lpfloat_t sample;
    
    if (!u->params.tape.osc) {
        return 0.0;
    }
    
    // Update parameters from connections or direct values
    if (u->param_sources[UPARAM_SPEED]) {
        u->params.tape.speed = u->param_sources[UPARAM_SPEED]->output * u->param_mults[UPARAM_SPEED] + u->param_adds[UPARAM_SPEED];
    } else {
        u->params.tape.speed = u->param_values[UPARAM_SPEED];
    }
    
    if (u->param_sources[UPARAM_PHASE]) {
        u->params.tape.phase = u->param_sources[UPARAM_PHASE]->output * u->param_mults[UPARAM_PHASE] + u->param_adds[UPARAM_PHASE];
    } else {
        u->params.tape.phase = u->param_values[UPARAM_PHASE];
    }
    
    // Update oscillator parameters
    u->params.tape.osc->speed = u->params.tape.speed;
    u->params.tape.osc->phase = u->params.tape.phase;
    u->params.tape.osc->start = u->params.tape.start;
    
    // Process tape oscillator
    LPTapeOsc.process(u->params.tape.osc);
    
    if (u->params.tape.osc->current_frame) {
        sample = u->params.tape.osc->current_frame->data[0];
    } else {
        sample = 0.0;
    }
    
    // Update phase back from oscillator
    u->params.tape.phase = u->params.tape.osc->phase;
    
    // Set outputs
    u->output = sample;
    u->outputs[0] = u->params.tape.speed;   // Speed output
    u->outputs[1] = u->params.tape.phase;   // Phase output
    u->num_outputs = 2;
    
    return sample;
}

void set_tape_ugen_param(ugen_t * u, int index, void * value) {
    lpfloat_t * v;
    lpbuffer_t * buf;

    switch(index) {
        case UTAPEIN_SPEED:
            v = (lpfloat_t *)value;
            u->param_values[UPARAM_SPEED] = *v;
            u->params.tape.speed = *v;
            break;

        case UTAPEIN_PHASE:
            v = (lpfloat_t *)value;
            u->param_values[UPARAM_PHASE] = *v;
            u->params.tape.phase = *v;
            break;

        case UTAPEIN_BUF:
            buf = (lpbuffer_t *)value;
            u->params.tape.buf = buf;
            u->params.tape.samplerate = buf->samplerate;
            if (u->params.tape.osc) {
                u->params.tape.osc->buf = buf;
                u->params.tape.osc->samplerate = buf->samplerate;
                u->params.tape.osc->range = buf->length - 1;
            }
            break;

        case UTAPEIN_START:
            v = (lpfloat_t *)value;
            u->param_values[UPARAM_START] = *v;
            u->params.tape.start = *v;
            if (u->params.tape.osc) {
                u->params.tape.osc->start = *v;
            }
            break;

        case UTAPEIN_RANGE:
            v = (lpfloat_t *)value;
            u->param_values[UPARAM_RANGE] = *v;
            if (u->params.tape.osc) {
                u->params.tape.osc->range = *v;
            }
            break;

        default:
            break;
    }
}

lpfloat_t get_tape_ugen_output(ugen_t * u, int index) {
    switch(index) {
        case UTAPEOUT_MAIN:
            return u->output;
        case UTAPEOUT_SPEED:
            return u->num_outputs > 0 ? u->outputs[0] : u->params.tape.speed;
        case UTAPEOUT_PHASE:
            return u->num_outputs > 1 ? u->outputs[1] : u->params.tape.phase;
        case UTAPEOUT_GATE:
            return 1.0; // TODO: implement gate logic
        default:
            return 0.0;
    }
}

ugen_t * create_tape_ugen(void) {
    ugen_t * u;
    lpbuffer_t * frame;
    
    u = (ugen_t *)LPMemoryPool.alloc(sizeof(ugen_t), 1);
    memset(u, 0, sizeof(ugen_t));
    
    u->type = UGEN_TAPE;
    u->params.tape.phase = 0.0;
    u->params.tape.speed = 1.0;
    u->params.tape.start = 0.0;
    u->params.tape.samplerate = 44100.0;
    u->params.tape.buf = NULL;
    
    // Create tape oscillator instance
    frame = LPBuffer.create(1, 1, 44100);
    u->params.tape.osc = LPTapeOsc.create(frame);
    
    // Set default parameter values
    u->param_values[UPARAM_SPEED] = 1.0;
    u->param_values[UPARAM_PHASE] = 0.0;
    u->param_values[UPARAM_START] = 0.0;
    u->param_values[UPARAM_PULSEWIDTH] = 0.5;
    u->param_values[UPARAM_RANGE] = 1.0;
    
    // Initialize multipliers and adds to unity/zero
    for (int i = 0; i < NUM_UGEN_PARAMS; i++) {
        u->param_mults[i] = 1.0;
        u->param_adds[i] = 0.0;
    }

    return u;
}

// Legacy wrapper functions - these just call the new interface
void process_tape_ugen(ugen_t * u) {
    lpugen_tape_process(u);
}

void destroy_tape_ugen(ugen_t * u) {
    // Clean up the tape oscillator
    if (u->params.tape.osc) {
        if (u->params.tape.osc->current_frame) {
            free(u->params.tape.osc->current_frame);
        }
        free(u->params.tape.osc);
    }
}
