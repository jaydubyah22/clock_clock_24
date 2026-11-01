# ClockClock24

A 24-hour digital clock drawn with 24 analog clock faces in Tkinter.
The original digit artwork is preserved: four digits, each made from a
two-column, three-row grid of clocks.

## Run

Requires Python 3.9 or newer with Tkinter. There are no third-party runtime
dependencies. Some Linux distributions provide Tkinter separately as `python3-tk`.

```sh
python3 main.py
python3 main.py --windowed
```

The default is fullscreen. Press **Escape** to leave fullscreen; close the
window to quit. Windowed mode resizes the clock to fit the available space.

Optionally install the application into a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
clock-clock-24 --windowed
```

## Motion and configuration

The clock holds the current HHMM display, then rotates to the next minute,
finishing at the minute boundary. All hands start and finish together.
Elapsed wall time determines position, so a delayed callback does not slow
down the clock. Waking from sleep or changing the system clock immediately
resynchronizes the display; it may jump to the new position.

Edit the immutable `Settings` dataclass in `settings.py` to change defaults,
or pass a `Settings` instance to `app.run`. Hour and minute speeds are maximum
degrees per second; the longest required movement determines the shared
duration. Refresh rate controls smoothness, not travel speed. `rotations`
specifies extra full clockwise turns in addition to the movement needed to
reach the target. Zero allows direct clockwise travel. Configurations that
cannot accommodate every movement within a minute are rejected before startup.

Angles use the original coordinate convention: 0° down, 90° right, 180° up,
and 270° left. Subtracting angles therefore moves clockwise.

## Structure

| Module | Responsibility |
| --- | --- |
| `data.py` | Immutable digit artwork |
| `model.py` | Time-to-digit mapping and grid geometry |
| `animation.py` | Pure interpolation, transitions, and minute scheduling |
| `settings.py` | Validated configuration |
| `app.py` | Canvas rendering, one timer, and window lifecycle |
| `main.py` | Command-line entry point |

Imports do not open windows. The model and animation modules have no Tkinter
dependency. The application accepts a clock function for deterministic testing.

## Validate

```sh
python3 -m unittest discover -v
```

Tests cover all 1,440 minute transitions in a day, speed limits, synchronized
arrival, midnight rollover, clock changes, geometry, persistent canvas items,
and timer cleanup. Tk integration tests use doubles and do not require a display;
they do not replace a visual check on the target operating system.

Optional development checks, after installing Ruff:

```sh
ruff check .
ruff format --check .
```

See [REVIEW.md](REVIEW.md) for the original findings and behavioral changes.
