#ifndef LP_UGENS_CORE_H
#define LP_UGENS_CORE_H

#include "pippicore.h"
#include "oscs.tape.h"
#include "oscs.pulsar.h"

// Ugen type enumeration
enum UgenTypes {
    UGEN_SINE,
    UGEN_TAPE,
    UGEN_ADC,
    UGEN_DAC,
    UGEN_MIX,
    UGEN_MULT,
    UGEN_PULSAR,
    NUM_UGEN_TYPES
};

// Parameter type enumeration (shared across all ugens)
enum UgenParams {
    // Basic parameters
    UPARAM_FREQ,
    UPARAM_PHASE, 
    UPARAM_AMP,
    UPARAM_GAIN,
    UPARAM_SPEED,
    UPARAM_CHANNEL,
    UPARAM_PULSEWIDTH,
    
    // Mult parameters
    UPARAM_A,  // for mult
    UPARAM_B,  // for mult

    // DAC parameters
    UPARAM_INPUT,  // for dac input signal
    
    // Tape parameters
    UPARAM_BUF,
    UPARAM_START,
    UPARAM_RANGE,
    
    // ADC parameters
    UPARAM_SMOOTHING,
    
    // Pulsar wavetable parameters
    UPARAM_WAVETABLES,
    UPARAM_WAVETABLE_LENGTH,
    UPARAM_NUM_WAVETABLES,
    UPARAM_WAVETABLE_OFFSETS,
    UPARAM_WAVETABLE_LENGTHS,
    UPARAM_WAVETABLE_MORPH,
    UPARAM_WAVETABLE_MORPH_FREQ,
    
    // Pulsar window parameters
    UPARAM_WINDOWS,
    UPARAM_WINDOW_LENGTH,
    UPARAM_NUM_WINDOWS,
    UPARAM_WINDOW_OFFSETS,
    UPARAM_WINDOW_LENGTHS,
    UPARAM_WINDOW_MORPH,
    UPARAM_WINDOW_MORPH_FREQ,
    
    // Pulsar burst parameters
    UPARAM_BURST,
    UPARAM_BURST_SIZE,
    UPARAM_BURST_POS,
    
    // Pulsar other parameters
    UPARAM_SATURATION,
    UPARAM_SAMPLERATE,
    
    NUM_UGEN_PARAMS
};

typedef struct ugen_t ugen_t;

typedef struct ugen_t {
    int type;                           // UGEN_SINE, UGEN_TAPE, etc.
    lpfloat_t output;                   // Main output value
    lpfloat_t outputs[8];               // Additional outputs (level, peak, freq, etc.)
    int num_outputs;                    // Number of additional outputs
    
    // Direct parameter connections to other ugens
    ugen_t * param_sources[NUM_UGEN_PARAMS];  // Source ugens for parameters
    lpfloat_t param_mults[NUM_UGEN_PARAMS];   // Scaling multipliers
    lpfloat_t param_adds[NUM_UGEN_PARAMS];    // Scaling offsets
    lpfloat_t param_values[NUM_UGEN_PARAMS];  // Direct parameter values
    uint32_t param_hashes[NUM_UGEN_PARAMS];   // Unique hash for shared memory params of param key in this style:
                                              //     <instrument_name>-<node_name>-<param_name>
    
    // Type-specific parameter storage
    union {
        struct {
            lpfloat_t phase;
            lpfloat_t samplerate;
        } sine;
        
        struct {
            lpfloat_t phase;
            lpfloat_t speed;
            lpfloat_t start;
            lpfloat_t samplerate;
            lpbuffer_t * buf;
            lptapeosc_t * osc;
        } tape;
        
        struct {
            int channel;
            lpfloat_t current_sample;
            lpfloat_t level_accumulator;
            lpfloat_t peak_level;
            lpfloat_t smoothing_factor;
        } adc;
        
        struct {
            int channel;
            lpfloat_t input_sample;      // Input from connected ugen
            lpfloat_t gain;              // Output gain
        } dac;

        struct {
            int channel;
            lpfloat_t current_sample;    // Current sample from async mixer
            lpfloat_t gain;              // Output gain
        } mix;

        struct {
            lpfloat_t a;
            lpfloat_t b;
        } mult;
        
        struct {
            lpfloat_t phase;
            lpfloat_t freq;
            lpfloat_t samplerate;
            lpfloat_t pulsewidth;
            lpfloat_t saturation;
            lppulsarosc_t * osc;
        } pulsar;
        
    } params;
} ugen_t;

// Streamlined factory interface
typedef struct ugen_factory_t {
    ugen_t * (*create)(char * instrument_name, char * node_name, int ugen_type);
    lpfloat_t (*process)(ugen_t * u);                    // Process and return main output
    void (*connect)(ugen_t * u, int param, ugen_t * source, lpfloat_t mult, lpfloat_t add);
    void (*set_param)(ugen_t * u, int param, lpfloat_t value);
    void (*set_param_buffer)(ugen_t * u, int param, lpbuffer_t * buffer);  // For complex buffer parameters
    lpfloat_t (*get_output)(ugen_t * u, int index);      // Get output by index (0=main)
    void (*destroy)(ugen_t * u);
} ugen_factory_t;

extern const ugen_factory_t LPUgen;

// Core ugen functions
ugen_t * lpugen_create(char * instrument_name, char * node_name, int ugen_type);
lpfloat_t lpugen_process(ugen_t * u);
void lpugen_connect(ugen_t * u, int param, ugen_t * source, lpfloat_t mult, lpfloat_t add);
void lpugen_set_param(ugen_t * u, int param, lpfloat_t value);
void lpugen_enable_external_param(ugen_t * u, int param, uint32_t hash);
void lpugen_set_param_buffer(ugen_t * u, int param, lpbuffer_t * buffer);
lpfloat_t lpugen_get_output(ugen_t * u, int index);
void lpugen_destroy(ugen_t * u);

// Helper function to get parameter value (either from connection or direct value)
lpfloat_t lpugen_get_param(ugen_t * u, int param);

// Type-specific process functions (implemented in separate files)
lpfloat_t lpugen_sine_process(ugen_t * u);
lpfloat_t lpugen_tape_process(ugen_t * u);
lpfloat_t lpugen_adc_process(ugen_t * u);
lpfloat_t lpugen_dac_process(ugen_t * u);
lpfloat_t lpugen_mult_process(ugen_t * u);
lpfloat_t lpugen_pulsar_process(ugen_t * u);

// ADC-specific helper functions
void lpugen_adc_set_input_sample(ugen_t * u, lpfloat_t sample);
lpfloat_t lpugen_adc_get_level(ugen_t * u);
lpfloat_t lpugen_adc_get_peak(ugen_t * u);

// DAC-specific helper functions
lpfloat_t lpugen_dac_get_output_sample(ugen_t * u, int channel);

// Type-specific creation functions
ugen_t * create_tape_ugen(void);
ugen_t * create_pulsar_ugen(void);

#endif
