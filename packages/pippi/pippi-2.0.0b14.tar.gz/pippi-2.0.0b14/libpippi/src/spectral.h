#ifndef LP_SPECTRAL_H
#define LP_SPECTRAL_H

#include "pippicore.h"
#include "fft/fft.h"

typedef struct lpspectral_factory_t {
    lpbuffer_t * (*convolve)(lpbuffer_t *, lpbuffer_t *);
    lpbuffer_t * (*process)(lpbuffer_t * snd, lpfloat_t length, lpbuffer_t * window, int (*callback)(lpfloat_t pos, lpbuffer_t * real, lpbuffer_t * imag), size_t blocksize);
} lpspectral_factory_t;

extern const lpspectral_factory_t LPSpectral;

#endif
