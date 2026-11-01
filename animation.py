import math


def rotation_distance(start_angle, end_angle, num_rotations):
    """Return the clockwise angular distance used by the existing animation."""
    return (start_angle - end_angle) + (360 * num_rotations)


def shared_frame_count(hour_distances, minute_distances, hour_speed, minute_speed):
    """Return one frame count long enough for every hand to reach its target.

    The configured speeds are treated as maximum degrees-per-frame values. The
    hand that needs the most frames determines the duration; all other hands
    interpolate across the same duration so they finish together.
    """
    if hour_speed <= 0 or minute_speed <= 0:
        raise ValueError("Rotation speeds must be greater than zero")

    required_frames = [distance / hour_speed for distance in hour_distances]
    required_frames.extend(distance / minute_speed for distance in minute_distances)

    return max(1, math.ceil(max(required_frames, default=0)))


def interpolated_angle(start_angle, distance, frame, total_frames):
    """Return the angle for a frame of a fixed-duration clockwise animation."""
    if total_frames <= 0:
        raise ValueError("total_frames must be greater than zero")

    progress = min(max(frame / total_frames, 0), 1)
    return (start_angle - (distance * progress)) % 360
