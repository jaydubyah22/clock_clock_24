"""Configuration without GUI side effects."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Settings:
    """Speeds are maximum degrees per second, independent of refresh rate."""

    width: int = 1600
    height: int = 900
    fullscreen: bool = True
    frame_interval_ms: int = 20
    hour_speed: float = 50.0
    minute_speed: float = 25.0
    rotations: int = 1
    hand_color: str = "#282828"

    def __post_init__(self) -> None:
        for name in ("width", "height", "frame_interval_ms"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name in ("hour_speed", "minute_speed"):
            value = getattr(self, name)
            if not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if (
            not isinstance(self.rotations, int)
            or isinstance(self.rotations, bool)
            or self.rotations < 0
        ):
            raise ValueError("rotations must be a nonnegative integer")
