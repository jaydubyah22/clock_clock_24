"""Digit layout and geometry regressions, requiring no display server."""

import unittest
from datetime import datetime

from data import DIGITS
from model import angles_for_time, grid_centers
from settings import Settings


class ModelTests(unittest.TestCase):
    def test_digit_artwork_has_six_faces_per_digit(self):
        self.assertEqual(len(DIGITS), 10)
        for digit in DIGITS:
            self.assertEqual(len(digit), 6)
            self.assertTrue(all(len(pair) == 2 for pair in digit))

    def test_leading_zero_and_column_order(self):
        state = angles_for_time(datetime(2026, 1, 1, 1, 23))
        expected = tuple((a % 360, b % 360) for digit in (0, 1, 2, 3) for a, b in DIGITS[digit])
        self.assertEqual(state, expected)
        self.assertEqual(len(state), 24)

    def test_grid_is_centered_and_column_major(self):
        centers = grid_centers(1600, 900, 70)
        self.assertEqual(len(centers), 24)
        self.assertEqual(centers[0][0], centers[2][0])
        self.assertEqual(centers[0][1], centers[3][1])
        self.assertAlmostEqual((centers[0][0] + centers[-1][0]) / 2, 800)
        self.assertAlmostEqual((centers[0][1] + centers[-1][1]) / 2, 450)

    def test_settings_reject_invalid_values(self):
        for name, value in (
            ("width", 0),
            ("height", -1),
            ("frame_interval_ms", 0),
            ("hour_speed", float("nan")),
            ("minute_speed", float("inf")),
            ("minute_speed", -1),
            ("rotations", -1),
            ("rotations", 1.5),
        ):
            with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                Settings(**{name: value})
