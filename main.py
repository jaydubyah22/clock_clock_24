"""Command-line entry point for ClockClock24."""

import argparse

from settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="A clock made from 24 animated clock faces.")
    parser.add_argument("--windowed", action="store_true", help="start in a resizable window")
    args = parser.parse_args()

    # Keep model imports and --help usable without Tk installed or a display.
    from app import run

    run(Settings(fullscreen=not args.windowed))


if __name__ == "__main__":
    main()
