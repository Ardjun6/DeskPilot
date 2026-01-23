from __future__ import annotations

from typing import Callable, Dict

import keyboard


class HotkeyRegistrationError(RuntimeError):
    """Raised when a hotkey cannot be registered."""


KEY_ALIASES = {
    "control": "ctrl",
    "ctl": "ctrl",
    "command": "win",
    "cmd": "win",
    "windows": "win",
    "option": "alt",
    "opt": "alt",
    "⌘": "win",
    "⌥": "alt",
    "⌃": "ctrl",
    "⇧": "shift",
}


def normalize_hotkey(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""
    cleaned = raw.replace(" ", "")
    parts = [part for part in cleaned.split("+") if part]
    normalized_parts = [KEY_ALIASES.get(part.lower(), part.lower()) for part in parts]
    return "+".join(normalized_parts)


def validate_hotkey(value: str) -> tuple[bool, str, str]:
    normalized = normalize_hotkey(value)
    if not normalized:
        return True, "", ""
    try:
        keyboard.parse_hotkey(normalized)
    except Exception as exc:  # noqa: BLE001
        return False, normalized, str(exc)
    return True, normalized, ""


class HotkeyManager:
    """Hotkey manager backed by the keyboard library."""

    def __init__(self) -> None:
        self._bindings: Dict[str, int] = {}

    def register(self, hotkey: str, callback: Callable[[], None]) -> None:
        normalized = normalize_hotkey(hotkey)
        if not normalized:
            raise HotkeyRegistrationError("Empty hotkey")
        if normalized in self._bindings:
            raise HotkeyRegistrationError(f"Hotkey already registered: {normalized}")
        try:
            keyboard.parse_hotkey(normalized)
            handler = keyboard.add_hotkey(normalized, callback)
        except Exception as exc:  # noqa: BLE001
            raise HotkeyRegistrationError(str(exc)) from exc
        self._bindings[normalized] = handler

    def unregister(self, hotkey: str) -> None:
        normalized = normalize_hotkey(hotkey)
        handler = self._bindings.pop(normalized, None)
        if handler is not None:
            keyboard.remove_hotkey(handler)

    def clear(self) -> None:
        for handler in self._bindings.values():
            keyboard.remove_hotkey(handler)
        self._bindings.clear()
