import unittest
from datetime import datetime, timedelta

from animation import (
    ClockTimeline,
    Transition,
    interpolated_angle,
    rotation_distance,
    shared_frame_count,
)
from model import angles_for_time
from settings import Settings


class AnimationTests(unittest.TestCase):
    def test_shared_frame_count_uses_slowest_hand(self):
        frames = shared_frame_count(
            hour_distances=[360, 450],
            minute_distances=[360, 540],
            hour_speed=1,
            minute_speed=0.5,
        )
        self.assertEqual(frames, 1080)

    def test_all_hands_reach_targets_on_same_final_frame(self):
        starts = [0, 90, 180, 270]
        ends = [90, 0, 270, 180]
        distances = [rotation_distance(start, end, 1) for start, end in zip(starts, ends)]
        frames = shared_frame_count(distances, distances, 1, 0.5)

        final_angles = [
            interpolated_angle(start, distance, frames, frames)
            for start, distance in zip(starts, distances)
        ]

        self.assertEqual(final_angles, ends)

    def test_interpolation_does_not_finish_early(self):
        start = 0
        end = 90
        distance = rotation_distance(start, end, 1)
        frames = 720

        penultimate = interpolated_angle(start, distance, frames - 1, frames)
        final = interpolated_angle(start, distance, frames, frames)

        self.assertNotEqual(penultimate, end)
        self.assertEqual(final, end)

    def test_invalid_speeds_are_rejected(self):
        with self.assertRaises(ValueError):
            shared_frame_count([360], [360], 0, 0.5)

    def test_rotation_wraps_negative_and_equivalent_angles(self):
        self.assertEqual(rotation_distance(-90, 270, 0), 0)
        self.assertEqual(rotation_distance(0, 90, 0), 270)
        self.assertEqual(rotation_distance(90, 0, 1), 450)
        with self.assertRaises(ValueError):
            rotation_distance(0, 90, -1)

    def test_interpolation_clamps_outside_the_transition(self):
        self.assertEqual(interpolated_angle(90, 450, -1, 10), 90)
        self.assertEqual(interpolated_angle(90, 450, 11, 10), 0)

    def test_transition_boundaries_and_empty_states(self):
        transition = Transition.between(((0, 90),), ((90, 0),), Settings())
        self.assertEqual(transition.at(-1), transition.start)
        self.assertEqual(transition.at(transition.duration), transition.target)
        self.assertNotEqual(transition.at(transition.duration / 2), transition.target)
        for start, end in (((), ()), (((0, 0),), ())):
            with self.assertRaises(ValueError):
                Transition.between(start, end, Settings())

    def test_zero_distance_transition(self):
        state = ((0, 90),)
        transition = Transition.between(state, state, Settings(rotations=0))
        self.assertEqual(transition.duration, 0)
        self.assertEqual(transition.at(0), state)

    def test_every_minute_transition_finishes_together_within_speed_limits(self):
        settings = Settings()
        midnight = datetime(2026, 1, 1)
        for minute in range(24 * 60):
            now = midnight + timedelta(minutes=minute)
            start = angles_for_time(now)
            target = angles_for_time(now + timedelta(minutes=1))
            transition = Transition.between(start, target, settings)
            with self.subTest(time=now):
                self.assertGreater(transition.duration, 0)
                self.assertLess(transition.duration, 60)
                self.assertEqual(transition.at(transition.duration), target)
                for hour, minute_distance in transition.distances:
                    self.assertLessEqual(hour / transition.duration, settings.hour_speed + 1e-9)
                    self.assertLessEqual(
                        minute_distance / transition.duration, settings.minute_speed + 1e-9
                    )

    def test_timeline_holds_current_time_then_animates_to_midnight(self):
        now = datetime(2026, 12, 31, 23, 59)
        settings = Settings()
        timeline = ClockTimeline(settings)
        transition = Transition.between(
            angles_for_time(now),
            angles_for_time(now + timedelta(minutes=1)),
            settings,
        )
        self.assertEqual(timeline.at(now), angles_for_time(now))
        halfway = now + timedelta(seconds=60 - transition.duration / 2)
        actual = timeline.at(halfway)
        expected = transition.at(transition.duration / 2)
        for actual_pair, expected_pair in zip(actual, expected):
            for angle, expected_angle in zip(actual_pair, expected_pair):
                # Angles either side of zero are equivalent on a circle.
                difference = (angle - expected_angle + 180) % 360 - 180
                self.assertAlmostEqual(difference, 0, places=4)
        boundary = now + timedelta(minutes=1)
        self.assertEqual(timeline.at(boundary), angles_for_time(boundary))

    def test_timeline_recovers_after_sleep_and_clock_changes(self):
        timeline = ClockTimeline(Settings())
        for now in (
            datetime(2026, 1, 1, 12, 0),
            datetime(2026, 1, 1, 15, 10),
            datetime(2026, 1, 1, 10, 0),
        ):
            self.assertEqual(timeline.at(now), angles_for_time(now))

    def test_impossible_timing_is_rejected_before_startup(self):
        with self.assertRaises(ValueError):
            ClockTimeline(Settings(minute_speed=1))


if __name__ == "__main__":
    unittest.main()
