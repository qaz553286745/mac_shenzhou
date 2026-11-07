#include "HaseeAudioDiagnostic.h"
#include <libkern/OSDebug.h>
#include <libkern/OSAtomic.h>
static volatile SInt32 gHaseeFailureCount = 0;
__attribute__((noinline))
void HaseeAudioFailure(unsigned code, const char *function, const char *reason)
{
    IOLog("[HASEE-AUDIO:E%03u] %s: %s\n", code, function, reason);
    const SInt32 ordinal = OSIncrementAtomic(&gHaseeFailureCount);
    if (ordinal < 4) {
        IOLog("[HASEE-AUDIO:BT-BEGIN] error=%u ordinal=%u\n", code, (unsigned)ordinal + 1);
        OSReportWithBacktrace("[HASEE-AUDIO:BACKTRACE] failure=%u function=%s", code, function);
        IOLog("[HASEE-AUDIO:BT-END] error=%u\n", code);
    } else if (ordinal == 4) {
        IOLog("[HASEE-AUDIO:BT-LIMIT] four failure backtraces already emitted\n");
    }
}
