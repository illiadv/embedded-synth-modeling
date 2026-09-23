#ifndef FM_H
#define FM_H

#include <stdbool.h>

#include "config.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    float carrier_frequency;
    float modulation_frequency;
    float d;
    bool active;
    float amplitude;
    float t;
} FM_Oscillator;

void FM_InitOsc(FM_Oscillator *osc, float carrier_freq, float modulation_freq, float d, float amplitude);
sound_sample_t FM_GetSample(FM_Oscillator *osc);

#ifdef __cplusplus
}
#endif

#endif
