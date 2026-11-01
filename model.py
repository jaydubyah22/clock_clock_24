"""Pure transformations between local time and the 24 clock faces.

Faces are ordered by column, then row. Angles follow the original artwork:
zero points down, 90 right, 180 up, and 270 left.
"""

from datetime import datetime
from typing import Tuple

from data import DIGITS

HandPair = Tuple[float, float]
ClockState = Tuple[HandPair, ...]
Point = Tuple[float, float]


def angles_for_time(value: datetime) -> ClockState:
    """Render a zero-padded, 24-hour HHMM value as 24 hand pairs."""
    return tuple(
        (hour % 360, minute % 360)
        for digit in value.strftime("%H%M")
        for hour, minute in DIGITS[int(digit)]
    )


def grid_centers(width: float, height: float, radius: float) -> Tuple[Point, ...]:
    """Center an eight-column, three-row grid with proportional spacing."""
    spacing = radius * 0.15
    pitch = radius * 2 + spacing
    left = (width - (8 * radius * 2 + 7 * spacing)) / 2 + radius
    top = (height - (3 * radius * 2 + 2 * spacing)) / 2 + radius
    return tuple(
        (left + column * pitch, top + row * pitch) for column in range(8) for row in range(3)
    )
