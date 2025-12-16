#include "ugens.core.h"
#include "ugens.sine.h"
#include "ugens.tape.h"
#include "ugens.pulsar.h"
#include "ugens.adc.h"
#include "ugens.dac.h"
#include "ugens.mix.h"
#include "ugens.mult.h"

#define DEFAULT_SAMPLERATE 48000

// Parameter name lookup table
static const char * UGEN_PARAM_NAMES[] = {
    "freq",                   // UPARAM_FREQ
    "phase",                  // UPARAM_PHASE
    "amp",                    // UPARAM_AMP
    "gain",                   // UPARAM_GAIN
    "speed",                  // UPARAM_SPEED
    "channel",                // UPARAM_CHANNEL
    "pulsewidth",             // UPARAM_PULSEWIDTH
    "a",                      // UPARAM_A
    "b",                      // UPARAM_B
    "in",                     // UPARAM_INPUT
    "buf",                    // UPARAM_BUF
    "start",                  // UPARAM_START
    "range",                  // UPARAM_RANGE
    "smoothing",              // UPARAM_SMOOTHING
    "wavetables",             // UPARAM_WAVETABLES
    "wavetable_length",       // UPARAM_WAVETABLE_LENGTH
    "num_wavetables",         // UPARAM_NUM_WAVETABLES
    "wavetable_offsets",      // UPARAM_WAVETABLE_OFFSETS
    "wavetable_lengths",      // UPARAM_WAVETABLE_LENGTHS
    "wavetable_morph",        // UPARAM_WAVETABLE_MORPH
    "wavetable_morph_freq",   // UPARAM_WAVETABLE_MORPH_FREQ
    "windows",                // UPARAM_WINDOWS
    "window_length",          // UPARAM_WINDOW_LENGTH
    "num_windows",            // UPARAM_NUM_WINDOWS
    "window_offsets",         // UPARAM_WINDOW_OFFSETS
    "window_lengths",         // UPARAM_WINDOW_LENGTHS
    "window_morph",           // UPARAM_WINDOW_MORPH
    "window_morph_freq",      // UPARAM_WINDOW_MORPH_FREQ
    "burst",                  // UPARAM_BURST
    "burst_size",             // UPARAM_BURST_SIZE
    "burst_pos",              // UPARAM_BURST_POS
    "saturation",             // UPARAM_SATURATION
    "samplerate"              // UPARAM_SAMPLERATE
};

// Factory instance
const ugen_factory_t LPUgen = {
    lpugen_create,
    lpugen_process,
    lpugen_connect,
    lpugen_set_param,
    lpugen_set_param_buffer,
    lpugen_get_output,
    lpugen_destroy
};

ugen_t * lpugen_create(char * instrument_name, char * node_name, int ugen_type) {
    uint32_t param_hash = 0;
    char param_key[LPMAXKEY] = {0};
    ugen_t * u = (ugen_t *)LPMemoryPool.alloc(1, sizeof(ugen_t));
    if (u == NULL) return NULL;

    
    // Initialize common fields
    u->type = ugen_type;
    u->output = 0.0f;
    u->num_outputs = 1;  // Default to just main output
    
    // Initialize parameter arrays
    for (int i = 0; i < NUM_UGEN_PARAMS; i++) {
        u->param_sources[i] = NULL;
        u->param_mults[i] = 1.0f;
        u->param_adds[i] = 0.0f;
        u->param_values[i] = 0.0f;

        // Create hash for potential external control
        // Format: <instrument>-<node>-<param_name>
        memset(param_key, 0, LPMAXKEY);
        if (i < NUM_UGEN_PARAMS && UGEN_PARAM_NAMES[i] != NULL) {
            snprintf(param_key, LPMAXKEY, "%s-%s-%s", instrument_name, node_name, UGEN_PARAM_NAMES[i]);
            param_hash = lphashstr(param_key);
            u->param_hashes[i] = param_hash;
        } else {
            u->param_hashes[i] = 0;
        }
    }
    
    for (int i = 0; i < 8; i++) {
        u->outputs[i] = 0.0f;
    }
    
    // Type-specific initialization
    switch (ugen_type) {
        case UGEN_SINE:
            u->params.sine.phase = 0.0f;
            u->params.sine.samplerate = DEFAULT_SAMPLERATE;
            u->param_values[UPARAM_FREQ] = 440.0f;  // Default frequency
            u->num_outputs = 3;  // main, freq, phase
            break;
            
        case UGEN_TAPE:
            u->params.tape.phase = 0.0f;
            u->params.tape.speed = 1.0f;
            u->params.tape.start = 0.0f;
            u->params.tape.samplerate = DEFAULT_SAMPLERATE;
            u->params.tape.buf = NULL;
            u->param_values[UPARAM_SPEED] = 1.0f;
            u->num_outputs = 3;  // main, speed, phase
            break;
            
        case UGEN_ADC:
            u->params.adc.channel = 0;
            u->params.adc.current_sample = 0.0f;
            u->params.adc.level_accumulator = 0.0f;
            u->params.adc.peak_level = 0.0f;
            u->params.adc.smoothing_factor = 0.1f;
            u->param_values[UPARAM_GAIN] = 1.0f;
            u->param_values[UPARAM_CHANNEL] = 0.0f;
            u->num_outputs = 5;  // main, level, peak, gain, channel
            break;
            
        case UGEN_DAC:
            u->params.dac.channel = 0;
            u->params.dac.input_sample = 0.0f;
            u->params.dac.gain = 1.0f;
            u->param_values[UPARAM_GAIN] = 1.0f;
            u->param_values[UPARAM_CHANNEL] = 0.0f;
            u->num_outputs = 3;  // main, gain, channel
            break;

        case UGEN_MIX:
            u->params.mix.channel = 0;
            u->params.mix.current_sample = 0.0f;
            u->params.mix.gain = 1.0f;
            u->param_values[UPARAM_GAIN] = 1.0f;
            u->param_values[UPARAM_CHANNEL] = 0.0f;
            u->num_outputs = 3;  // main, gain, channel
            break;

        case UGEN_MULT:
            u->param_values[UPARAM_A] = 1.0f;
            u->param_values[UPARAM_B] = 1.0f;
            u->num_outputs = 3;  // main, a, b
            break;
            
        case UGEN_PULSAR:
            u->params.pulsar.phase = 0.0f;
            u->params.pulsar.freq = 440.0f;
            u->params.pulsar.samplerate = DEFAULT_SAMPLERATE;
            u->params.pulsar.pulsewidth = 0.5f;
            u->params.pulsar.saturation = 1.0f;
            u->params.pulsar.osc = LPPulsarOsc.create();  // Start with no wavetables/windows
            u->param_values[UPARAM_FREQ] = 440.0f;
            u->param_values[UPARAM_PULSEWIDTH] = 0.5f;
            u->param_values[UPARAM_SATURATION] = 1.0f;
            u->num_outputs = 3;  // main, freq, phase
            break;
            
        default:
            LPMemoryPool.free(u);
            return NULL;
    }
    
    return u;
}

lpfloat_t lpugen_get_param(ugen_t * u, int param) {
    if (param < 0 || param >= NUM_UGEN_PARAMS) return 0.0f;
    
    lpfloat_t value;
    
    // Get value from connected source, session external source, or direct value
    if (u->param_sources[param] != NULL) {
        // Priority 1: Connected ugen modulation source
        value = u->param_sources[param]->output;
    } else if (u->param_hashes[param] != 0) {
        // Priority 2: External session-based control (read from param_values cache)
        // NOTE: param_values is updated per-block in the stream callback
        value = u->param_values[param];
    } else {
        // Priority 3: Direct static value
        value = u->param_values[param];
    }
    
    // Apply scaling
    return value * u->param_mults[param] + u->param_adds[param];
}

lpfloat_t lpugen_process(ugen_t * u) {
    if (u == NULL) return 0.0f;
    
    // Process all connected parameter sources first
    for (int i = 0; i < NUM_UGEN_PARAMS; i++) {
        if (u->param_sources[i] != NULL) {
            lpugen_process(u->param_sources[i]);
        }
    }
    
    // Call type-specific process function
    switch (u->type) {
        case UGEN_SINE:
            u->output = lpugen_sine_process(u);
            break;
        case UGEN_TAPE:
            u->output = lpugen_tape_process(u);
            break;
        case UGEN_ADC:
            u->output = lpugen_adc_process(u);
            break;
        case UGEN_DAC:
            u->output = lpugen_dac_process(u);
            break;
        case UGEN_MIX:
            u->output = lpugen_mix_process(u);
            break;
        case UGEN_MULT:
            u->output = lpugen_mult_process(u);
            break;
        case UGEN_PULSAR:
            u->output = lpugen_pulsar_process(u);
            break;
        default:
            u->output = 0.0f;
    }
    
    return u->output;
}

void lpugen_connect(ugen_t * u, int param, ugen_t * source, lpfloat_t mult, lpfloat_t add) {
    if (u == NULL || param < 0 || param >= NUM_UGEN_PARAMS) return;
    
    u->param_sources[param] = source;
    u->param_mults[param] = mult;
    u->param_adds[param] = add;
}

void lpugen_set_param(ugen_t * u, int param, lpfloat_t value) {
    if (u == NULL || param < 0 || param >= NUM_UGEN_PARAMS) return;

    u->param_values[param] = value;
    // Clear any existing connection
    u->param_sources[param] = NULL;
    u->param_mults[param] = 1.0f;
    u->param_adds[param] = 0.0f;
}

void lpugen_enable_external_param(ugen_t * u, int param, uint32_t hash) {
    if (u == NULL || param < 0 || param >= NUM_UGEN_PARAMS) return;
    u->param_hashes[param] = hash;
}

void lpugen_set_param_buffer(ugen_t * u, int param, lpbuffer_t * buffer) {
    if (u == NULL || buffer == NULL || param < 0 || param >= NUM_UGEN_PARAMS) return;
    
    // Handle buffer parameters based on type and parameter
    switch (u->type) {
        case UGEN_TAPE:
            if (param == UPARAM_BUF) {
                u->params.tape.buf = buffer;
                u->params.tape.samplerate = buffer->samplerate;
            }
            break;
        case UGEN_PULSAR:
            if (param == UPARAM_WAVETABLES && u->params.pulsar.osc) {
                u->params.pulsar.osc->wavetables[0] = buffer;
                // FIXME When setting wavetables, we may need to update related parameters
                // The caller should also set num_wavetables, onsets, and lengths separately
            } else if (param == UPARAM_WINDOWS && u->params.pulsar.osc) {
                u->params.pulsar.osc->windows[0] = buffer;
                // FIXME When setting windows, we may need to update related parameters
                // The caller should also set num_windows, onsets, and lengths separately
            }
            break;
        default:
            // For other types, buffer parameters aren't supported
            break;
    }
}

lpfloat_t lpugen_get_output(ugen_t * u, int index) {
    if (u == NULL || index < 0) return 0.0f;
    
    if (index == 0) {
        return u->output;  // Main output
    } else if (index < u->num_outputs) {
        return u->outputs[index - 1];  // Additional outputs
    }
    
    return 0.0f;
}

void lpugen_destroy(ugen_t * u) {
    if (u == NULL) return;
    
    // Type-specific cleanup
    switch (u->type) {
        case UGEN_TAPE:
            // Don't free the buffer - it's managed elsewhere
            break;
        default:
            break;
    }
    
    LPMemoryPool.free(u);
}
