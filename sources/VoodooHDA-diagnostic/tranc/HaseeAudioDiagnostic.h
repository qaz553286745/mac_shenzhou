#ifndef HASEE_AUDIO_DIAGNOSTIC_H
#define HASEE_AUDIO_DIAGNOSTIC_H
#include <IOKit/IOLib.h>
#define HASEE_AUDIO_STAGE(code, fmt, ...) \
    IOLog("[HASEE-AUDIO:S%03u] %s: " fmt "\n", (unsigned)(code), __FUNCTION__, ##__VA_ARGS__)
void HaseeAudioFailure(unsigned code, const char *function, const char *reason);
#define HASEE_AUDIO_FAIL(code, reason) HaseeAudioFailure((code), __FUNCTION__, (reason))
#endif
