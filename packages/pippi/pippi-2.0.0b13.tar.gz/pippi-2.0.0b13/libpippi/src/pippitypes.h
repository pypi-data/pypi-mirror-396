/* TYPES */
#ifdef LP_FLOAT
typedef float lpfloat_t;
#else
typedef double lpfloat_t;
#endif

typedef int lpint_t;

/* Core datatypes */
typedef struct lpbuffer_t {
    size_t length;
    int samplerate;
    int channels;

    /* used for different types of playback */
    lpfloat_t phase;
    size_t boundary;
    size_t range;
    size_t pos;
    size_t onset;
    int is_looping;
    lpfloat_t data[];
} lpbuffer_t;

typedef struct lparray_t {
    int * data;
    size_t length;
    lpfloat_t phase;
} lparray_t;

/* This smoother was ported from sndkit with 
 * minimal changes. Thanks, Paul! 
 *
 * The implementation is explained in detail here:
 *     https://pbat.ch/sndkit/smoother/
 */
typedef struct lpsmoother_t {
    lpfloat_t smooth;
    lpfloat_t a1, b0, y0, psmooth;
    lpfloat_t onedsr;
} lpsmoother_t;


/* This filter type is shared among the butterworth 
 * filters ported from Paul Batchelor's Soundpipe.
 * The original Soundpipe annotation is preserved below.
 *
 * Original Author(s): Paris Smaragdis, John ffitch
 * Year: 1994
 * Location: Opcodes/butter.c
 */
typedef struct lpbfilter_t {
    lpfloat_t sr, freq, istor;
    lpfloat_t lkf;
    lpfloat_t a[8];
    lpfloat_t pidsr;
} lpbfilter_t;

/*
 * lpbalance_t is part of the LPFX.balance routine, ported directly 
 * from Paul Batchelor's Soundpipe, in turn ported from the csound opcode.
 *
 * RIP Barry Vercoe.
 *
 * The original Soundpipe annotation is preserved below.
 *
 * This code has been extracted from the Csound opcode "balance".
 * It has been modified to work as a Soundpipe module.
 *
 * Original Author(s): Barry Vercoe, john ffitch, Gabriel Maldonado
 * Year: 1991
 * Location: OOps/ugens5.c
 */
typedef struct lpbalance_t {
    lpfloat_t asig, csig, ihp;
    lpfloat_t c1, c2, prvq, prvr, prva;
} lpbalance_t;

/* Bandlimited interpolation by Liquid City Motors Will */
typedef struct lpbli_t {
    int quality;
    int samples_per_0x;
    int filter_length;
    int wrap;
    lpfloat_t * filter_table;
    int table_length;
    lpfloat_t resampling_factor;
} lpbli_t;
