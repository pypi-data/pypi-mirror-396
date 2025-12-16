#include "pippi.h"
#include "ugens.pulsar.h"
#include "oscs.pulsar.h"

// New unified interface implementation
lpfloat_t lpugen_pulsar_process(ugen_t * u) {
    lpfloat_t sample;
    
    if (!u->params.pulsar.osc) {
        return 0.0;
    }
    
    // Update parameters from connections or direct values
    if (u->param_sources[UPARAM_FREQ]) {
        u->params.pulsar.freq = u->param_sources[UPARAM_FREQ]->output * u->param_mults[UPARAM_FREQ] + u->param_adds[UPARAM_FREQ];
    } else {
        u->params.pulsar.freq = u->param_values[UPARAM_FREQ];
    }
    
    if (u->param_sources[UPARAM_PHASE]) {
        u->params.pulsar.phase = u->param_sources[UPARAM_PHASE]->output * u->param_mults[UPARAM_PHASE] + u->param_adds[UPARAM_PHASE];
    } else {
        u->params.pulsar.phase = u->param_values[UPARAM_PHASE];
    }
    
    if (u->param_sources[UPARAM_PULSEWIDTH]) {
        u->params.pulsar.pulsewidth = u->param_sources[UPARAM_PULSEWIDTH]->output * u->param_mults[UPARAM_PULSEWIDTH] + u->param_adds[UPARAM_PULSEWIDTH];
    } else {
        u->params.pulsar.pulsewidth = u->param_values[UPARAM_PULSEWIDTH];
    }
    
    // Update oscillator parameters
    u->params.pulsar.osc->freq = u->params.pulsar.freq;
    u->params.pulsar.osc->phase = u->params.pulsar.phase;
    u->params.pulsar.osc->pulsewidth = u->params.pulsar.pulsewidth;
    u->params.pulsar.osc->saturation = u->params.pulsar.saturation;
    u->params.pulsar.osc->samplerate = u->params.pulsar.samplerate;
    
    // Process pulsar oscillator
    sample = LPPulsarOsc.process(u->params.pulsar.osc);
    
    // Update phase back from oscillator
    u->params.pulsar.phase = u->params.pulsar.osc->phase;
    
    // Set outputs
    u->output = sample;
    u->outputs[0] = u->params.pulsar.freq;   // Freq output
    u->outputs[1] = u->params.pulsar.phase;  // Phase output
    u->num_outputs = 2;
    
    return sample;
}

void set_pulsar_ugen_param(ugen_t * u, int index, void * value) {
    int * i;
    lpfloat_t * v;

    switch(index) {
        case UPULSARIN_FREQ:
            v = (lpfloat_t *)value;
            u->param_values[UPARAM_FREQ] = *v;
            u->params.pulsar.freq = *v;
            break;

        case UPULSARIN_PHASE:
            v = (lpfloat_t *)value;
            u->param_values[UPARAM_PHASE] = *v;
            u->params.pulsar.phase = *v;
            break;

        case UPULSARIN_PULSEWIDTH:
            v = (lpfloat_t *)value;
            u->param_values[UPARAM_PULSEWIDTH] = *v;
            u->params.pulsar.pulsewidth = *v;
            break;

        case UPULSARIN_SATURATION:
            v = (lpfloat_t *)value;
            u->params.pulsar.saturation = *v;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->saturation = *v;
            }
            break;

        case UPULSARIN_SAMPLERATE:
            v = (lpfloat_t *)value;
            u->params.pulsar.samplerate = *v;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->samplerate = *v;
            }
            break;

        // Wavetable parameters - use buffer parameter handling via LPUgen factory
        case UPULSARIN_WTTABLE:
            // FIXME
            // This should now be handled via LPUgen.set_param_buffer(u, UPARAM_WAVETABLES, buffer)
            // But for legacy compatibility, we still accept it here
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->wavetables[0] = (lpbuffer_t *)value;
            }
            break;

        case UPULSARIN_NUMWTS:
            i = (int *)value;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->num_wavetables = *i;
            }
            break;

        case UPULSARIN_WTMORPH:
            v = (lpfloat_t *)value;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->wavetable_morph = *v;
            }
            break;

        case UPULSARIN_WTMORPHFREQ:
            v = (lpfloat_t *)value;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->wavetable_morph_freq = *v;
            }
            break;
            
        // Window parameters - use buffer parameter handling via LPUgen factory
        case UPULSARIN_WINTABLE:
            // FIXME This should now be handled via LPUgen.set_param_buffer(u, UPARAM_WINDOWS, buffer)
            // But for legacy compatibility, we still accept it here
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->windows[0] = (lpbuffer_t *)value;
            }
            break;

        case UPULSARIN_NUMWINS:
            i = (int *)value;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->num_windows = *i;
            }
            break;

        case UPULSARIN_WINMORPH:
            v = (lpfloat_t *)value;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->window_morph = *v;
            }
            break;

        case UPULSARIN_WINMORPHFREQ:
            v = (lpfloat_t *)value;
            if (u->params.pulsar.osc) {
                u->params.pulsar.osc->window_morph_freq = *v;
            }
            break;

        default:
            break;
    }
}

lpfloat_t get_pulsar_ugen_output(ugen_t * u, int index) {
    switch(index) {
        case UPULSAROUT_MAIN:
            return u->output;
        case UPULSAROUT_FREQ:
            return u->num_outputs > 0 ? u->outputs[0] : u->params.pulsar.freq;
        case UPULSAROUT_PHASE:
            return u->num_outputs > 1 ? u->outputs[1] : u->params.pulsar.phase;
        case UPULSAROUT_PULSEWIDTH:
            return u->params.pulsar.pulsewidth;
        case UPULSAROUT_SATURATION:
            return u->params.pulsar.saturation;
        case UPULSAROUT_SAMPLERATE:
            return u->params.pulsar.samplerate;
        default:
            return 0.0;
    }
}

ugen_t * create_pulsar_ugen(void) {
    ugen_t * u;
    
    u = (ugen_t *)LPMemoryPool.alloc(sizeof(ugen_t), 1);
    memset(u, 0, sizeof(ugen_t));
    
    u->type = UGEN_PULSAR;
    u->params.pulsar.phase = 0.0;
    u->params.pulsar.freq = 440.0;
    u->params.pulsar.samplerate = 44100.0;
    u->params.pulsar.pulsewidth = 0.5;
    u->params.pulsar.saturation = 1.0;
    
    // Create pulsar oscillator instance
    u->params.pulsar.osc = LPPulsarOsc.create();
    
    // Set default parameter values
    u->param_values[UPARAM_FREQ] = 440.0;
    u->param_values[UPARAM_PHASE] = 0.0;
    u->param_values[UPARAM_PULSEWIDTH] = 0.5;
    
    // Initialize multipliers and adds to unity/zero
    for (int i = 0; i < NUM_UGEN_PARAMS; i++) {
        u->param_mults[i] = 1.0;
        u->param_adds[i] = 0.0;
    }

    return u;
}

// Legacy wrapper functions - these just call the new interface
void process_pulsar_ugen(ugen_t * u) {
    lpugen_pulsar_process(u);
}

void destroy_pulsar_ugen(ugen_t * u) {
    // Clean up the pulsar oscillator
    if (u->params.pulsar.osc) {
        free(u->params.pulsar.osc);
    }
}
