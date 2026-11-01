"""Exercise Tk integration through doubles without opening a window."""

import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from app import ClockApplication, ClockView, hand_endpoint
from model import angles_for_time
from settings import Settings


class ApplicationTests(unittest.TestCase):
    def test_single_timer_and_idempotent_shutdown(self):
        root = Mock()
        root.after.return_value = "timer-1"
        view = Mock()
        now = datetime(2026, 1, 1, 12, 0)
        application = ClockApplication(root, view, Settings(), now=lambda: now)
        application.start()
        application.start()
        root.after.assert_called_once()
        view.render.assert_called_once_with(angles_for_time(now))

        # Simulate the next Tk callback; it should schedule exactly one successor.
        callback = root.after.call_args.args[1]
        root.after.reset_mock()
        callback()
        root.after.assert_called_once()
        application.close()
        application.close()
        application.start()
        root.after_cancel.assert_called_once_with("timer-1")
        root.destroy.assert_called_once()
        self.assertEqual(root.after.call_count, 1)

    def test_render_reuses_all_48_hands_and_resize_preserves_state(self):
        canvas = Mock()
        canvas.create_line.side_effect = range(1000)
        view = ClockView(canvas, Settings())
        state = angles_for_time(datetime(2026, 1, 1, 12, 34))
        view.render(state)
        resize = canvas.bind.call_args.args[1]
        resize(SimpleNamespace(width=1600, height=900))
        self.assertEqual(canvas.create_line.call_count, 48)
        self.assertEqual(canvas.coords.call_count, 48)
        canvas.reset_mock()
        view.render(state)
        canvas.create_line.assert_not_called()
        canvas.delete.assert_not_called()
        self.assertEqual(canvas.coords.call_count, 48)

        canvas.reset_mock()
        resize(SimpleNamespace(width=800, height=450))
        self.assertEqual(canvas.create_line.call_count, 48)
        self.assertEqual(canvas.coords.call_count, 48)

    def test_endpoint_preserves_original_angle_convention(self):
        for angle, expected in ((0, (10, 30)), (90, (20, 20)), (180, (10, 10)), (270, (0, 20))):
            with self.subTest(angle=angle):
                actual = hand_endpoint((10, 20), angle, 10)
                self.assertAlmostEqual(actual[0], expected[0])
                self.assertAlmostEqual(actual[1], expected[1])

    def test_panel_and_shadows_fit_small_and_tall_windows(self):
        for width, height in ((400, 200), (1600, 900), (600, 1200)):
            with self.subTest(width=width, height=height):
                canvas = Mock()
                ClockView(canvas, Settings())
                resize = canvas.bind.call_args.args[1]
                resize(SimpleNamespace(width=width, height=height))
                for call in canvas.create_rectangle.call_args_list:
                    x1, y1, x2, y2 = call.args
                    self.assertGreaterEqual(x1, 0)
                    self.assertGreaterEqual(y1, 0)
                    self.assertLessEqual(x2, width)
                    self.assertLessEqual(y2, height)
