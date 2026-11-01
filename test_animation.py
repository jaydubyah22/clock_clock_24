import unittest

from animation import interpolated_angle, rotation_distance, shared_frame_count


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


if __name__ == "__main__":
    unittest.main()
