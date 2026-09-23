#include <math.h>

#include "fm.h"

void FM_InitOsc(FM_Oscillator *osc, float carrier_freq, float modulation_freq, float d, float amplitude)
{
    osc->carrier_frequency = carrier_freq;
    osc->modulation_frequency = modulation_freq;
    osc->d = d;
    osc->amplitude = amplitude;
    osc->t = 0.0f;
    osc->active = true;
}

sound_sample_t FM_GetSample(FM_Oscillator *osc)
{
    float value;

    float a = 2 * 3.14592f * osc->carrier_frequency;
    float b = 2 * 3.14592f * osc->modulation_frequency;

    float I = osc->d / osc->modulation_frequency;

    // e = Asin (at + I sin bt)
    value = osc->amplitude * sin(a * osc->t + I * sin(b * osc->t));

    osc->t += (1.0f / SAMPLING_RATE);

    return (sound_sample_t)(value * MAX_SAMPLE_VALUE);
}
