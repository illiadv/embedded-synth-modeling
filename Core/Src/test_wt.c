#include "test.h"
#include "wavetable.h"

WT_Oscillator wt_osc;

void Test_Init()
{
    WT_GenerateTables();
    WT_InitOsc(&wt_osc, 220.0f, 0, 1.0f);
}

sound_sample_t Test_GetSample()
{
    return WT_GetSampleLerp(&wt_osc);
}
