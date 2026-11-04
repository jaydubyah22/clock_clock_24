#ifndef CLOCKCLOCK_STYLE_SELECTION_H
#define CLOCKCLOCK_STYLE_SELECTION_H
#include <stdbool.h>
#include <stdint.h>
#include "Choreography.h"

typedef struct {
    bool initialized;
    int64_t minute;
    int style;
} CCStyleSelection;

// Cache one random choice per minute so redraws never change choreography.
// The random function returns a uniform value below its argument.
static inline int ccStyleForMinute(CCStyleSelection *selection, int64_t minute,
                                  uint32_t (*randomBelow)(uint32_t)) {
    if (!selection->initialized || selection->minute != minute) {
        int style;
        if (!selection->initialized) {
            style = (int)randomBelow(CC_STYLE_COUNT);
        } else {
            // Map nine equally likely choices onto all styles except the last.
            style = (int)randomBelow(CC_STYLE_COUNT - 1);
            if (style >= selection->style) style++;
        }
        selection->initialized = true;
        selection->minute = minute;
        selection->style = style;
    }
    return selection->style;
}
#endif
