from __future__ import annotations

from typing import Callable, Dict


class HotkeyManager:
    """Placeholder hotkey manager; to be implemented with keyboard."""

    def __init__(self) -> None:
        self._bindings: Dict[str, Callable[[], None]] = {}

    def register(self, hotkey: str, callback: Callable[[], None]) -> None:
        # TODO: integrate with keyboard library and conflict detection
        self._bindings[hotkey] = callback

    def unregister(self, hotkey: str) -> None:
        self._bindings.pop(hotkey, None)

    def clear(self) -> None:
        self._bindings.clear()
