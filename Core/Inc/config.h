#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>

#ifndef TABLE_LENGTH
#define TABLE_LENGTH 512
#define TABLE_WRAP (TABLE_LENGTH - 1)
#endif

#ifndef SAMPLING_RATE
#define SAMPLING_RATE 8000
#endif

#ifndef MAX_SAMPLE_VALUE
#define MAX_SAMPLE_VALUE INT16_MAX
#endif

#ifndef MIN_SAMPLE_VALUE
#define MIN_SAMPLE_VALUE INT16_MIN
#endif

#ifndef SAMPLE_TYPE
#define SAMPLE_TYPE int16_t
#endif

typedef SAMPLE_TYPE sound_sample_t;

#endif
