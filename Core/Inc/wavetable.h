#ifndef WAVETABLE_H
#define WAVETABLE_H

#include <stdbool.h>
#include "config.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    int table;
    uint32_t increment;
    uint32_t phase;
    bool active;
    float amplitude;
} WT_Oscillator;

void WT_InitOsc(WT_Oscillator *osc, float frequency, int table, float amplitude);
void WT_GenerateTables();
void WT_SetFrequency(WT_Oscillator *osc, float frequency);
sound_sample_t WT_GetSample(WT_Oscillator *osc);
sound_sample_t WT_GetSampleLerp(WT_Oscillator *osc);
sound_sample_t *WT_GetTable(int index);

#ifdef __cplusplus
}
#endif

#endif
