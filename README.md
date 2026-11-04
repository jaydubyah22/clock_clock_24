# ClockClock24

A native macOS screensaver inspired by ClockClock24, with 24 clock faces and
48 hands forming the local 24-hour time. Ten original animations are chosen randomly each minute, featuring
waves, opposing gears, ripples, spirals, mirrored formations, and reversals.
Hands vary their speed and direction, then slow smoothly into position at the
minute boundary.

## Install the macOS screensaver

**Requires macOS 11 or later. Supports Apple Silicon and Intel.**
No Python or additional software is needed for the download.

1. [Download ClockClock24 for macOS](https://github.com/jaydubyah22/clock_clock_24/raw/refs/heads/main/downloads/ClockClock24-macOS.zip).
2. Double-click the ZIP in Finder to extract **ClockClock24.saver**.
3. Double-click **ClockClock24.saver** and choose **Install for this user only**
   if macOS offers that choice.
4. Open **System Settings → Screen Saver**, select **ClockClock24** (usually
   under **Other**), and choose **Preview**. On older macOS versions, use
   **System Preferences → Desktop & Screen Saver**.

The current time holds for 32 seconds; movement fills the final 28 seconds
before the next minute. Leave the preview running to see the transitions.
Each minute chooses randomly from the ten animations, without repeating the
previous animation. The order changes each session; seeing all ten may take
longer than ten minutes.

The bundle is locally ad-hoc signed, rather than Apple-notarized. If macOS
blocks it, try Control-click → **Open** in Finder; if available, use
**System Settings → Privacy & Security → Open Anyway** after attempting to
open it. Only approve the download if you trust its source. You can also build
the screensaver yourself using the instructions below.

### Manual install or update

After extracting the ZIP into Downloads, quit System Settings and run:

```sh
mkdir -p "$HOME/Library/Screen Savers"
ditto "$HOME/Downloads/ClockClock24.saver" "$HOME/Library/Screen Savers/ClockClock24.saver"
```

Reopen System Settings and select ClockClock24. When updating, exit any running
screensaver preview first. If the old animation still appears, log out and back
in so macOS reloads the bundle.

### Verify the download

Download the [SHA-256 checksum](downloads/ClockClock24-macOS.zip.sha256).
From the folder containing the ZIP, compare its output with the checksum file:

```sh
shasum -a 256 ClockClock24-macOS.zip
```

### Build from source

Install Apple's Command Line Tools (`xcode-select --install`), then:

```sh
git clone https://github.com/jaydubyah22/clock_clock_24.git
cd clock_clock_24
sh macos/build.sh
mkdir -p "$HOME/Library/Screen Savers"
ditto macos/build/ClockClock24.saver "$HOME/Library/Screen Savers/ClockClock24.saver"
```

See [macOS documentation](macos/README.md) for the ten animations and motion tests.

### Uninstall

Select another screensaver, quit System Settings, and move
`~/Library/Screen Savers/ClockClock24.saver` to the Trash.
In Finder, use **Go → Go to Folder** to open `~/Library/Screen Savers`.

This is an independent project inspired by Humans since 1982's ClockClock24;
it is not affiliated with or endorsed by its creators.

---

## Python application

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
