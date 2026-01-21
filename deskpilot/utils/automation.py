from __future__ import annotations

import time
from typing import Iterable

import pyautogui

pyautogui.FAILSAFE = True


def safe_sleep(seconds: float) -> None:
    """Sleep with a small guard to keep UI responsive."""
    time.sleep(max(seconds, 0.0))


def play_steps(steps: Iterable[dict]) -> None:
    """Placeholder for macro playback with pyautogui."""
    for _step in steps:
        safe_sleep(0.05)
        # TODO: implement concrete actions per step
