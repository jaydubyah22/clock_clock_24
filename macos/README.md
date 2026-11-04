# ClockClock24 for macOS

Native ScreenSaverView port created from this repository's digit artwork.
Uses local 24-hour time, with ten choreographies that finish together at each
minute boundary. The current time holds for 32 seconds, followed by 28 seconds
of movement with a gentle, progressive slowdown into the next time. Supports previews, resizing, and waking from
sleep without Python or third-party dependencies.

Build with Apple's Command Line Tools:

```sh
sh macos/build.sh
ditto macos/build/ClockClock24.saver "$HOME/Library/Screen Savers/ClockClock24.saver"
```

Open System Settings > Screen Saver, find ClockClock24 (usually under Other),
and select it. Reopen System Settings if it was open during installation.
The bundle is locally ad-hoc signed; it is not a notarized distribution.
The universal binary supports Apple Silicon and Intel Macs running macOS 11+.

`Digits.h` contains the digit artwork from `data.py`. `Choreography.h` contains
stateless motion sampling, so previews and waking from sleep use the same phase.
The ten sequences cycle once every ten minutes:

1. **Silk sweep** — clockwise turns with faster and slower paired hands.
2. **Counterpoint** — paired hands turn in opposite directions at different speeds.
3. **Travelling wave** — columns release left to right, with the middle row reversed.
4. **Meshing gears** — neighbouring faces counter-rotate at varied speeds.
5. **Pond ripple** — a centre-out release with faster outer hands.
6. **Vortex** — spiral release with faster rotation near the edges.
7. **Pendulum** — hands sweep out, come to rest, then reverse into the digits.
8. **Venetian blinds** — rows fan into angled formations before folding into time.
9. **Butterfly** — mirrored halves sweep into a vertical formation, then reveal time.
10. **Cascade** — a diagonal release through an angled formation into the digits.

Quintic easing gives each movement zero velocity and acceleration at its endpoints.
Staggered starts and different travel distances vary the speeds; all hands complete
the transition at the minute boundary. The Python application is unchanged.

These are original sequences inspired by the collective choreography described in
the [ClockClock24 manual](https://clockforward.com/content/manuals/humans-since-1982-clockclock-24.pdf),
not reproductions of the physical clock's choreography.

Run the motion checks (all ten styles, every minute including midnight, final
slowdown, and frame continuity):

```sh
xcrun clang -Wall -Wextra -Werror macos/tests/choreography.c -o /tmp/clockclock24-choreography-test
/tmp/clockclock24-choreography-test
```

Implementation follows Apple's ScreenSaverView API:
https://developer.apple.com/documentation/screensaver/screensaverview

To uninstall, select another screen saver and remove
`~/Library/Screen Savers/ClockClock24.saver`.
