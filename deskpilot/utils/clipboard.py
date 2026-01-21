from __future__ import annotations

from typing import Optional

import pyperclip
from PySide6.QtGui import QGuiApplication


def copy_text(text: str) -> None:
    """Copy text to clipboard using pyperclip with Qt fallback."""
    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)


def get_text() -> Optional[str]:
    """Retrieve text from clipboard."""
    try:
        return pyperclip.paste()
    except pyperclip.PyperclipException:
        clipboard = QGuiApplication.clipboard()
        return clipboard.text() if clipboard is not None else None
