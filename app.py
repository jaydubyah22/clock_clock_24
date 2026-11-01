"""Tk rendering and application lifecycle."""

import math
import tkinter as tk
from datetime import datetime
from typing import Callable, List, Optional, Tuple

from animation import ClockTimeline
from model import ClockState, Point, grid_centers
from settings import Settings


class ClockView:
    """Own canvas items; animation changes existing hand coordinates."""

    def __init__(self, canvas: tk.Canvas, settings: Settings) -> None:
        self.canvas = canvas
        self.settings = settings
        self._state: ClockState = ()
        self._centers: Tuple[Point, ...] = ()
        self._hands: List[Tuple[int, ...]] = []
        self._radius = 1.0
        canvas.bind("<Configure>", self._resize)

    def _resize(self, event: tk.Event) -> None:
        # Leave room for the panel border and its offset shadow on every edge.
        self._radius = max(1.0, min(event.width / 20, event.height / 9))
        self._centers = grid_centers(event.width, event.height, self._radius)
        self.canvas.delete("all")
        self._hands.clear()
        radius = self._radius
        hand_width = max(1, radius * 0.1)
        left, top = self._centers[0]
        right, bottom = self._centers[-1]
        border = radius * 1.5
        shadow = radius * 0.5
        self.canvas.create_rectangle(
            left - border - shadow,
            top - border + shadow,
            right + border - shadow,
            bottom + border + shadow,
            fill="light grey",
            outline="light grey",
        )
        self.canvas.create_rectangle(
            left - border,
            top - border,
            right + border,
            bottom + border,
            fill="#FAFAFA",
            outline="light grey",
        )
        for x, y in self._centers:
            offset = radius * 0.06
            self.canvas.create_oval(
                x - radius - offset,
                y - radius + offset,
                x + radius - offset,
                y + radius + offset,
                fill="light grey",
                outline="light grey",
            )
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="#F0F0F0",
                outline="light grey",
                width=max(1, radius / 30),
            )
            hands = tuple(
                self.canvas.create_line(
                    x,
                    y,
                    x,
                    y,
                    fill=self.settings.hand_color,
                    width=hand_width,
                    capstyle=tk.BUTT,
                )
                for _ in range(2)
            )
            self._hands.append(hands)
            # The circular hub rounds the inner ends; outer tips remain square.
            dot_radius = hand_width / 2
            self.canvas.create_oval(
                x - dot_radius,
                y - dot_radius,
                x + dot_radius,
                y + dot_radius,
                fill=self.settings.hand_color,
                outline="",
            )
        self.render(self._state)

    def render(self, state: ClockState) -> None:
        self._state = state
        for center, hands, angles in zip(self._centers, self._hands, state):
            for hand, angle in zip(hands, angles):
                endpoint = hand_endpoint(center, angle, self._radius * 0.891)
                self.canvas.coords(hand, *center, *endpoint)


def hand_endpoint(center: Point, angle: float, length: float) -> Point:
    radians = math.radians(angle)
    return (
        center[0] + math.sin(radians) * length,
        center[1] + math.cos(radians) * length,
    )


class ClockApplication:
    """One callback updates all 48 hands and is cancelled on close."""

    def __init__(
        self,
        root: tk.Tk,
        view: ClockView,
        settings: Settings,
        now: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.root = root
        self.view = view
        self.settings = settings
        self.now = now
        self.timeline = ClockTimeline(settings)
        self._callback: Optional[str] = None
        self._closed = False
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

    def start(self) -> None:
        if self._callback is None and not self._closed:
            self._tick()

    def _tick(self) -> None:
        self._callback = None
        self.view.render(self.timeline.at(self.now()))
        self._callback = self.root.after(self.settings.frame_interval_ms, self._tick)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._callback is not None:
            self.root.after_cancel(self._callback)
            self._callback = None
        self.root.destroy()


def run(settings: Settings) -> None:
    # Fail before constructing a window if animation settings are invalid.
    ClockTimeline(settings)
    root = tk.Tk()
    root.title("ClockClock24")
    root.geometry(f"{settings.width}x{settings.height}")
    root.minsize(400, 200)
    root.attributes("-fullscreen", settings.fullscreen)
    canvas = tk.Canvas(root, background="white", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    application = ClockApplication(root, ClockView(canvas, settings), settings)
    application.start()
    root.mainloop()
