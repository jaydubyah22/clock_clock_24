"""Time-based, synchronized animation without a dependency on Tk."""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Sequence

from model import ClockState, angles_for_time
from settings import Settings


def rotation_distance(start_angle: float, end_angle: float, num_rotations: int) -> float:
    """Clockwise distance with the requested number of extra complete turns."""
    if not isinstance(num_rotations, int) or num_rotations < 0:
        raise ValueError("num_rotations must be a nonnegative integer")
    return (start_angle - end_angle) % 360 + 360 * num_rotations


def shared_frame_count(
    hour_distances: Sequence[float],
    minute_distances: Sequence[float],
    hour_speed: float,
    minute_speed: float,
) -> int:
    """Compatibility helper for speeds expressed in degrees per frame."""
    if any(not math.isfinite(speed) or speed <= 0 for speed in (hour_speed, minute_speed)):
        raise ValueError("Rotation speeds must be finite and greater than zero")
    durations = [distance / hour_speed for distance in hour_distances]
    durations.extend(distance / minute_speed for distance in minute_distances)
    return max(1, math.ceil(max(durations, default=0)))


def interpolated_angle(
    start_angle: float, distance: float, frame: float, total_frames: float
) -> float:
    """Interpolate clockwise; frame and duration may also be elapsed seconds."""
    if not math.isfinite(total_frames) or total_frames <= 0:
        raise ValueError("total_frames must be finite and greater than zero")
    progress = min(max(frame / total_frames, 0), 1)
    return (start_angle - distance * progress) % 360


@dataclass(frozen=True)
class Transition:
    """A duration determined by the slowest hand synchronizes every movement."""

    start: ClockState
    target: ClockState
    distances: ClockState
    duration: float

    @classmethod
    def between(cls, start: ClockState, target: ClockState, settings: Settings) -> "Transition":
        if len(start) != len(target) or not start:
            raise ValueError("States must contain the same nonzero number of faces")
        distances = tuple(
            (
                rotation_distance(old[0], new[0], settings.rotations),
                rotation_distance(old[1], new[1], settings.rotations),
            )
            for old, new in zip(start, target)
        )
        duration = max(
            max(hour / settings.hour_speed, minute / settings.minute_speed)
            for hour, minute in distances
        )
        if duration >= 60:
            raise ValueError(
                "Hand speeds and rotations must allow a transition in under 60 seconds"
            )
        return cls(start, target, distances, duration)

    def at(self, elapsed: float) -> ClockState:
        if elapsed >= self.duration:
            return self.target
        if elapsed <= 0:
            return self.start
        return tuple(
            (
                interpolated_angle(angles[0], distances[0], elapsed, self.duration),
                interpolated_angle(angles[1], distances[1], elapsed, self.duration),
            )
            for angles, distances in zip(self.start, self.distances)
        )


class ClockTimeline:
    """Hold the current time, then arrive at the next minute boundary.

    Sampling wall time makes delayed frames and waking from sleep catch up
    immediately. Only the transition for the current minute is cached.
    """

    def __init__(self, settings: Settings) -> None:
        maximum_distance = 360 * (settings.rotations + 1)
        if maximum_distance / min(settings.hour_speed, settings.minute_speed) >= 60:
            raise ValueError("Hand speeds are too low for the configured rotations")
        self.settings = settings
        self._minute: Optional[datetime] = None
        self._transition: Optional[Transition] = None

    def at(self, now: datetime) -> ClockState:
        minute = now.replace(second=0, microsecond=0)
        if minute != self._minute:
            self._transition = Transition.between(
                angles_for_time(minute),
                angles_for_time(minute + timedelta(minutes=1)),
                self.settings,
            )
            self._minute = minute
        assert self._transition is not None
        elapsed = (now - minute).total_seconds()
        return self._transition.at(elapsed - (60 - self._transition.duration))
