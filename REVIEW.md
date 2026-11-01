# Refactoring review

The original project captured the artwork well, but application state, rendering,
and timing were tightly coupled. This revision keeps the small application small:
standard-library runtime, a handful of focused modules, and no framework.

## Findings and fixes

| Finding | Consequence | Change |
| --- | --- | --- |
| Importing `settings` constructs Tk objects; importing `main` starts the event loop | Tests and reuse require a running desktop | Pure settings and an explicit entry point |
| Angle calculations mutate several global lists | Correctness depends on calling functions in the right order | Immutable states returned by pure functions |
| Each hand owns a chain of timer callbacks | Shared frame counts do not guarantee simultaneous real-time updates | One callback samples time and renders all hands |
| Hands are deleted and recreated on every frame | Repeated allocation and unnecessary canvas churn | Persistent line items updated with `coords` |
| A 5-second/55-second cycle begins at launch | Digits do not change at the actual minute boundary | A wall-clock timeline arriving at each boundary |
| Animation duration counts callbacks | Event-loop delays change travel speed | Interpolation from elapsed seconds |
| Rotation distance uses unnormalized signed angles | Equivalent angles can take different paths; zero turns can move backward | Modular clockwise distances and explicit extra turns |
| Hard-coded screen dimensions determine layout | Fullscreen layouts can be clipped or off-center | Layout recalculated on canvas resize |
| Time parsing and digit lookup use many intermediate lists | Data flow is hard to follow | Direct HHMM formatting and table lookup |
| Configuration is a group of mutable module globals | Invalid speeds and timing combinations fail late | Frozen, validated configuration |
| No explicit callback cleanup | Lifecycle behavior is hard to reason about | Idempotent shutdown cancels the pending callback |

## Intentional behavior changes

Transitions now finish at the actual next minute rather than showing that minute
early on a launch-relative schedule. Starting the app during a transition shows
the position appropriate to that instant. Missed frames are skipped rather than
replayed; changes to wall time can cause an immediate jump.

Speeds retain the old nominal maxima (1° and 0.5° per 20 ms become 50°/s and
25°/s). Rotation counts now mean extra full turns plus the clockwise remainder,
so some hands travel farther than before. Every hand still shares one duration
and remains within its speed limit. The digit shapes and angle convention are
unchanged.

The renderer retains the pale panel, face shadows, and dark hands, scales them
with the window, and uses rounded hand caps. Fullscreen remains the default;
Escape and a windowed CLI option make development and use easier.

## Validation limits

The deterministic suite exercises the model and Tk integration through doubles.
A real desktop run remains necessary to assess platform-specific Tk appearance,
fullscreen behavior, and perceived smoothness. There is no claim of visual
verification from the automated tests.
