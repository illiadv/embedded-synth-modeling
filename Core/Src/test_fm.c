#include "test.h"
#include "fm.h"

FM_Oscillator fm_osc;

void Test_Init()
{
    FM_InitOsc(&fm_osc, 220.0f, 100.0f, 50.0f, 1.0f);
}

sound_sample_t Test_GetSample()
{
    return FM_GetSample(&fm_osc);
}
