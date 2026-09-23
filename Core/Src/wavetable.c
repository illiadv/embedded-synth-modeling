#include <math.h>

#include "wavetable.h"

sound_sample_t sinewaveTable[TABLE_LENGTH] = {0};
sound_sample_t sawtoothTable[TABLE_LENGTH] = {0};
sound_sample_t triangleTable[TABLE_LENGTH] = {0};

sound_sample_t* tables[3] = {sinewaveTable, sawtoothTable, triangleTable};

void WT_InitOsc(WT_Oscillator *osc, float frequency, int table, float amplitude)
{
    osc->table = table;
    osc->amplitude = amplitude;
    osc->active = true;
    osc->phase = 0.0f;
    osc->increment = 0.0f;

    WT_SetFrequency(osc, frequency);
}

void WT_GenerateTables()
{
    for (int i = 0; i < TABLE_LENGTH; i++)
    {
	sinewaveTable[i] = (sin(i* 2 * 3.141592f / TABLE_LENGTH)) * (MAX_SAMPLE_VALUE);

	sawtoothTable[i] = ((float)i / TABLE_LENGTH * 2 - 1.0f) * MAX_SAMPLE_VALUE;

	float v = (i < TABLE_LENGTH / 2) ? (float)i : TABLE_LENGTH - (float)i;
	v = v * 2;
	v = v / TABLE_LENGTH * 2 - 1.0f;
	triangleTable[i] = v * MAX_SAMPLE_VALUE;
    }
}

sound_sample_t *WT_GetTable(int index)
{
    return tables[index];
}

void WT_SetFrequency(WT_Oscillator *osc, float frequency)
{
    osc->increment = (uint32_t)((frequency * 0x100000000) / SAMPLING_RATE);
}


sound_sample_t WT_GetSample(WT_Oscillator *osc)
{
    if (!osc->active)
	return 0;

    sound_sample_t outputValue = 0;

    int index = osc->phase >> 23;
    float y = tables[osc->table][index];
    outputValue = (sound_sample_t)(y * osc->amplitude);

    osc->phase += osc->increment;

    return outputValue;
}

sound_sample_t WT_GetSampleLerp(WT_Oscillator *osc)
{
    if (!osc->active)
	return 0;

    sound_sample_t outputValue = 0;

    int x0 = osc->phase >> 23;
    int x1 = (x0 + 1) & TABLE_WRAP;

    float y0 = tables[osc->table][x0];
    float y1 = tables[osc->table][x1];

    float f = (osc->phase & 0x7FFFFF) / (float)0x800000;
    float y = y0 + (y1 - y0) * f;

    outputValue = (sound_sample_t)(y * osc->amplitude);

    osc->phase += osc->increment;

    return outputValue;
}
