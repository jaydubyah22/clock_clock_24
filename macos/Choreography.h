#ifndef CLOCKCLOCK_CHOREOGRAPHY_H
#define CLOCKCLOCK_CHOREOGRAPHY_H
#include <math.h>

#define CC_STYLE_COUNT 10
#define CC_TRANSITION_SECONDS 28.0

// Stateless wall-clock sampling keeps previews, wake, and dropped frames in sync.
static inline double ccClamp(double x) { return fmax(0.0, fmin(1.0, x)); }
static inline double ccEase(double x) {
    x = ccClamp(x);
    // Quintic easing has zero velocity and acceleration at both ends.
    return x * x * x * (10.0 + x * (-15.0 + 6.0 * x));
}
static inline double ccTravel(double start, double end, int direction, double turns) {
    double distance = fmod(direction * (end - start), 360.0);
    if (distance < 0) distance += 360.0;
    return direction * (distance + floor(turns + 0.5) * 360.0);
}
static inline double ccAngle(int style, int face, int hand,
                             double start, double end, double progress) {
    int col = face / 3, row = face % 3;
    double x = col / 7.0, y = row / 2.0;
    double radius = hypot((col - 3.5) / 3.5, row - 1.0) / sqrt(2.0);
    int direction = -1;
    double delay = 0, turns = 1, waypoint = 180, split = 0.48;
    switch (style % CC_STYLE_COUNT) {
        case 0: // Silk sweep: two clockwise speeds, shared arrival.
            turns = hand == 0 ? 2 : 1;
            break;
        case 1: // Counterpoint: each pair unwinds in opposite directions.
            direction = hand == 0 ? -1 : 1;
            turns = hand == 0 ? 1 : 2;
            break;
        case 2: // Travelling wave: staggered release from left to right.
            delay = 0.24 * x;
            direction = row == 1 ? 1 : -1;
            turns = 1 + 0.5 * hand;
            break;
        case 3: // Meshing gears: neighbouring faces counter-rotate.
            direction = (col + row) % 2 ? 1 : -1;
            turns = 1 + 0.5 * ((row + hand) % 3);
            break;
        case 4: // Pond ripple: the centre releases the outer faces.
            delay = 0.25 * radius;
            direction = hand == 0 ? -1 : 1;
            turns = 1 + radius;
            break;
        case 5: // Vortex: a spatial spiral, with a faster outer edge.
            delay = 0.12 * (atan2(row - 1.0, col - 3.5) + M_PI) / (2 * M_PI);
            direction = -1;
            turns = 1 + 1.5 * radius + 0.35 * hand;
            break;
        case 6: // Pendulum: sweep out, pause, then reverse into the digits.
            direction = hand == 0 ? -1 : 1;
            waypoint = start + direction * (210 + 60 * y);
            split = 0.42;
            break;
        case 7: // Venetian blinds: rows fan open, then fold into time.
            delay = 0.07 * row;
            direction = row == 1 ? 1 : -1;
            waypoint = 90 + row * 45 + hand * 180;
            split = 0.52;
            break;
        case 8: // Butterfly: mirrored wings meet in a vertical formation.
            delay = 0.18 * (1 - fabs(2 * x - 1));
            direction = col < 4 ? -1 : 1;
            waypoint = hand == 0 ? 0 : 180;
            split = 0.46;
            break;
        case 9: // Cascade: a diagonal formation pours into the new time.
            delay = 0.22 * (col + row) / 9.0;
            direction = hand == 0 ? 1 : -1;
            waypoint = 45 + col * 30 + row * 45 + hand * 180;
            split = 0.55;
            break;
    }
    double t = ccClamp((progress - delay) / (1 - delay));
    if (style < 6) {
        return start + ccTravel(start, end, direction, turns) * ccEase(t);
    }
    double middle = start + ccTravel(start, waypoint, direction, 0);
    int finishDirection = style == 6 ? -direction : direction;
    if (t < split) return start + (middle - start) * ccEase(t / split);
    return middle + ccTravel(middle, end, finishDirection, 0) *
        ccEase((t - split) / (1 - split));
}
#endif
