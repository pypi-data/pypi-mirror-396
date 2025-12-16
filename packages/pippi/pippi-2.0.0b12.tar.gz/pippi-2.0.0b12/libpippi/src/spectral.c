#include "spectral.h"

/* TODO for use in the user-supplied callbacks (and some built-ins maybe?)
int spectral_polar_to_xy(lpbuffer_t * mag, lpbuffer_t * arg, lpbuffer_t * real, lpbuffer_t * imag);
int spectral_xy_to_polar(lpbuffer_t * real, lpbuffer_t * imag, lpbuffer_t * mag, lpbuffer_t * arg);
*/

int spectral_passthrough_callback(lpfloat_t pos, 
        __attribute__((unused)) lpbuffer_t * real, 
        __attribute__((unused)) lpbuffer_t * imag) {
    printf("LPSpectral.process :: callback @ pos=%f\n", pos);
    return 0;
}

int spectral_transform(lpbuffer_t * snd, lpbuffer_t * real, lpbuffer_t * imag, lpfloat_t * realc, lpfloat_t * imagc) {
    size_t i = 0;
    int c = 0;

    if(snd == NULL || real == NULL || imag == NULL) {
        return -1;
    }

    for(c=0; c < snd->channels; c++) {
        for(i=0; i < snd->length; i++) {
            realc[i] = snd->data[i * snd->channels + c];
            imagc[i] = 0;
        }

        Fft_transform(realc, imagc, snd->length);

        for(i=0; i < snd->length; i++) {
            real->data[i * snd->channels + c] = lpzapgremlins(realc[i]);
            imag->data[i * snd->channels + c] = lpzapgremlins(imagc[i]);
        }
    }

    return 0;
}

int spectral_itransform(lpbuffer_t * real, lpbuffer_t * imag, lpfloat_t * realc, lpfloat_t * imagc, lpbuffer_t * out) {
    size_t i = 0;
    int c = 0;

    if(out == NULL || real == NULL || imag == NULL || out->length != real->length || out->length != imag->length) {
        return -1;
    }

    for(c=0; c < out->channels; c++) {
        for(i=0; i < out->length; i++) {
            realc[i] = real->data[i * out->channels + c];
            imagc[i] = imag->data[i * out->channels + c];
        }

        Fft_inverseTransform(realc, imagc, out->length);

        for(i=0; i < out->length; i++) {
            out->data[i * out->channels + c] = lpzapgremlins(realc[i]);
        }
    }

    return 0;
}

lpbuffer_t * spectral_process(lpbuffer_t * snd, 
        lpfloat_t length, 
        lpbuffer_t * window, 
        int (*callback)(lpfloat_t pos, lpbuffer_t * real, lpbuffer_t * imag), 
        size_t blocksize) {
    size_t i=0, read_pos=0, elapsed=0, framelength=length * (size_t)snd->samplerate;
    int c = 0;
    lpfloat_t sample=0, win_value=0, pos=0, mag=0;

    if(snd == NULL || length <= 0 || window == NULL || blocksize <= 0) return NULL;

    lpbuffer_t * block = LPBuffer.create(blocksize, snd->channels, snd->samplerate);
    lpbuffer_t * real = LPBuffer.create(blocksize, snd->channels, snd->samplerate);
    lpbuffer_t * imag = LPBuffer.create(blocksize, snd->channels, snd->samplerate);
    lpbuffer_t * out = LPBuffer.create(framelength, snd->channels, snd->samplerate);

    /* for per-channel processing in loop */
    lpfloat_t * realc = LPMemoryPool.alloc(blocksize, sizeof(lpfloat_t));
    lpfloat_t * imagc = LPMemoryPool.alloc(blocksize, sizeof(lpfloat_t));

    if(callback == NULL) callback = spectral_passthrough_callback;

    while(elapsed < framelength) {
        pos = elapsed / (lpfloat_t)framelength;
        mag = 0;

        read_pos = elapsed;
        if(read_pos + blocksize >= snd->length) break; // overflow...
                                                       
        // fill block with segment
        for(i=0; i < blocksize; i++) {
            win_value = LPInterpolation.linear(window, ((lpfloat_t)i/blocksize) * window->length);
            for(c=0; c < snd->channels; c++) {
                sample = snd->data[read_pos * snd->channels + c];
                mag = fmax(fabs(sample), mag);
                block->data[i * snd->channels + c] = sample * win_value;
            }
            read_pos += 1;
        }

        if(spectral_transform(block, real, imag, realc, imagc) < 0) {
            elapsed += blocksize/2;
            continue;
        }

        if(callback(pos, real, imag) < 0) {
            elapsed += blocksize/2;
            continue;
        }

        if(spectral_itransform(real, imag, realc, imagc, block) < 0) {
            elapsed += blocksize/2;
            continue;
        }

        // dub block into output
        LPFX.norm(block, mag);
        LPBuffer.dub(out, block, elapsed);

        // overlap/add...
        elapsed += blocksize/2;
    }

    LPBuffer.destroy(block);
    LPBuffer.destroy(real);
    LPBuffer.destroy(imag);
    LPMemoryPool.free(realc);
    LPMemoryPool.free(imagc);

    return out;
}

/* FIXME: handle multichannel audio */
lpbuffer_t * convolve_spectral(lpbuffer_t * src, lpbuffer_t * impulse) {
    size_t length, i;
    int c, impc;
    lpfloat_t mag;
    lpbuffer_t * out;
    lpbuffer_t * impchan;
    lpbuffer_t * srcchan;
    lpbuffer_t * outchan;

    length = src->length + impulse->length + 1;
    out = LPBuffer.create(length, src->channels, src->samplerate);
    mag = LPBuffer.mag(src);

    for(c=0; c < src->channels; c++) {
        impc = c % impulse->channels;
        outchan = LPBuffer.create(length, 1, src->samplerate);
        //srcchan = LPBuffer.create(src->length, 1, src->samplerate);
        //impchan = LPBuffer.create(impulse->length, 1, src->samplerate);
        srcchan = LPBuffer.create(length, 1, src->samplerate);
        impchan = LPBuffer.create(length, 1, src->samplerate);


        for(i=0; i < src->length; i++) {
            srcchan->data[i] = src->data[i * src->channels + c];
        }

        for(i=0; i < impulse->length; i++) {
            impchan->data[i] = impulse->data[i * impulse->channels + impc];
        }

        Fft_convolveReal(srcchan->data, impchan->data, outchan->data, length);
        for(i=0; i < length; i++) {
            out->data[i * src->channels + c] = outchan->data[i];
        }

        LPBuffer.destroy(outchan);
        LPBuffer.destroy(srcchan);
        LPBuffer.destroy(impchan);
    }

    LPFX.norm(out, mag);

    return out;
}

const lpspectral_factory_t LPSpectral = { convolve_spectral, spectral_process };
