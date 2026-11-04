#include <assert.h>
#include <stdio.h>
#include "../Choreography.h"
#include "../Digits.h"

static double angleError(double a, double b) { return fabs(remainder(a - b, 360)); }
int main(void) {
    double largestStep = 0;
    // Every minute of the day, including 23:59 -> 00:00, for every style.
    for (int minute = 0; minute < 1440; minute++) {
        int next = (minute + 1) % 1440;
        int from[] = {minute / 60 / 10, minute / 60 % 10, minute % 60 / 10, minute % 10};
        int to[] = {next / 60 / 10, next / 60 % 10, next % 60 / 10, next % 10};
        for (int style = 0; style < CC_STYLE_COUNT; style++) {
            for (int face = 0; face < 24; face++) {
                for (int hand = 0; hand < 2; hand++) {
                    double start = digits[from[face / 6]][face % 6][hand];
                    double end = digits[to[face / 6]][face % 6][hand];
                    assert(angleError(ccAngle(style, face, hand, start, end, -1), start) < 1e-9);
                    assert(angleError(ccAngle(style, face, hand, start, end, 1), end) < 1e-9);
                    assert(angleError(ccAngle(style, face, hand, start, end, 2), end) < 1e-9);
                    double last = ccAngle(style, face, hand, start, end, 1 - 0.02 / CC_TRANSITION_SECONDS);
                    // Last frame approaches the destination with effectively zero velocity.
                    assert(angleError(last, end) < 0.001);
                }
            }
        }
    }
    // Full frame-by-frame runs at 50Hz, checking reversals and stage boundaries.
    for (int style = 0; style < CC_STYLE_COUNT; style++) {
        int positive = 0, negative = 0;
        for (int face = 0; face < 24; face++) {
            for (int hand = 0; hand < 2; hand++) {
                double previous = ccAngle(style, face, hand, 90, -45, 0);
                for (int frame = 1; frame <= 1400; frame++) {
                    double angle = ccAngle(style, face, hand, 90, -45, frame / 1400.0);
                    double step = angle - previous;
                    assert(isfinite(angle));
                    assert(fabs(step) < 4.0);
                    if (step > 0.001) positive = 1;
                    if (step < -0.001) negative = 1;
                    largestStep = fmax(largestStep, fabs(step));
                    previous = angle;
                }
            }
        }
        if (style != 0 && style != 5) assert(positive && negative);
    }
    printf("PASS: all ten styles, all 1,440 minute changes, exact endpoints and soft landings.\n");
    printf("Largest 50Hz frame movement: %.3f degrees.\n", largestStep);
    return 0;
}
