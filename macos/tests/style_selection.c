#include <assert.h>
#include <stdio.h>
#include "../StyleSelection.h"

static uint32_t nextRandom, expectedBound;
static int calls;
static uint32_t randomBelow(uint32_t bound) {
    assert(bound == expectedBound);
    assert(nextRandom < bound);
    calls++;
    return nextRandom;
}

int main(void) {
    // Every style can be the first choice, including at epoch minute zero.
    for (int first = 0; first < CC_STYLE_COUNT; first++) {
        CCStyleSelection selection = {0};
        nextRandom = (uint32_t)first;
        expectedBound = CC_STYLE_COUNT;
        assert(ccStyleForMinute(&selection, 0, randomBelow) == first);
        int before = calls;
        for (int frame = 0; frame < 3000; frame++)
            assert(ccStyleForMinute(&selection, 0, randomBelow) == first);
        assert(calls == before);

        // Every other style is reachable exactly once, with no repeat bias.
        int seen[CC_STYLE_COUNT] = {0};
        for (int choice = 0; choice < CC_STYLE_COUNT - 1; choice++) {
            selection = (CCStyleSelection){true, 1439, first};
            nextRandom = (uint32_t)choice;
            expectedBound = CC_STYLE_COUNT - 1;
            int style = ccStyleForMinute(&selection, 1440, randomBelow);
            assert(style >= 0 && style < CC_STYLE_COUNT && style != first);
            seen[style]++;
        }
        for (int style = 0; style < CC_STYLE_COUNT; style++)
            assert(seen[style] == (style != first));
    }

    // Sleep, backwards clock changes, and negative epoch minutes all reselect.
    CCStyleSelection selection = {true, 100, 0};
    const int64_t minutes[] = {10000, 99, -1, 0};
    nextRandom = 0;
    expectedBound = CC_STYLE_COUNT - 1;
    for (unsigned i = 0; i < sizeof(minutes) / sizeof(minutes[0]); i++) {
        int previous = selection.style, before = calls;
        int style = ccStyleForMinute(&selection, minutes[i], randomBelow);
        assert(style != previous && calls == before + 1);
        assert(ccStyleForMinute(&selection, minutes[i], randomBelow) == style);
        assert(calls == before + 1);
    }
    puts("PASS: all random choices, no consecutive repeats, stable frames, midnight, wake and clock changes.");
    return 0;
}
