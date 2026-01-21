from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class Theme:
    name: str
    is_dark: bool
    colors: Dict[str, str]


THEMES: Dict[str, Theme] = {
    "dark": Theme(
        name="Dark",
        is_dark=True,
        colors={
            "bg": "#1f2227",
            "bg_alt": "#252932",
            "surface": "#2c3038",
            "border": "#3a3f4a",
            "text": "#f0f2f5",
            "text_muted": "#a9afbf",
            "accent": "#5b8def",
            "accent_soft": "#3b4a6a",
            "shadow": "#00000040",
            "input_bg": "#2c3038",
        },
    ),
    "light": Theme(
        name="Light",
        is_dark=False,
        colors={
            "bg": "#f7f8fb",
            "bg_alt": "#eef0f4",
            "surface": "#ffffff",
            "border": "#dfe3eb",
            "text": "#1f2430",
            "text_muted": "#6b7280",
            "accent": "#3b6cf6",
            "accent_soft": "#e7edff",
            "shadow": "#00000026",
            "input_bg": "#ffffff",
        },
    ),
    "classic": Theme(
        name="Classic",
        is_dark=False,
        colors={
            "bg": "#e8eaed",
            "bg_alt": "#dfe1e5",
            "surface": "#f5f6f7",
            "border": "#c9ccd3",
            "text": "#1f2430",
            "text_muted": "#555b66",
            "accent": "#4b6ea9",
            "accent_soft": "#dfe8f5",
            "shadow": "#00000020",
            "input_bg": "#ffffff",
        },
    ),
}


class ThemeManager:
    """Central theme controller with runtime switching."""

    def __init__(self, app: QApplication, default: str = "dark") -> None:
        self.app = app
        self.current = THEMES.get(default, list(THEMES.values())[0])
        self.apply(self.current)

    def set_theme(self, key: str) -> None:
        if key == "auto":
            palette = self.app.palette()
            is_dark = palette.window().color().value() < 128
            key = "dark" if is_dark else "light"
        theme = THEMES.get(key, self.current)
        self.apply(theme)

    def apply(self, theme: Theme) -> None:
        self.current = theme
        self._apply_palette(theme)
        self.app.setStyleSheet(self._build_qss(theme))

    def _apply_palette(self, theme: Theme) -> None:
        pal = self.app.palette()
        pal.setColor(QPalette.Window, QColor(theme.colors["bg"]))
        pal.setColor(QPalette.Base, QColor(theme.colors["input_bg"]))
        pal.setColor(QPalette.AlternateBase, QColor(theme.colors["bg_alt"]))
        pal.setColor(QPalette.Text, QColor(theme.colors["text"]))
        pal.setColor(QPalette.WindowText, QColor(theme.colors["text"]))
        pal.setColor(QPalette.Button, QColor(theme.colors["surface"]))
        pal.setColor(QPalette.ButtonText, QColor(theme.colors["text"]))
        pal.setColor(QPalette.ToolTipBase, QColor(theme.colors["surface"]))
        pal.setColor(QPalette.ToolTipText, QColor(theme.colors["text"]))
        pal.setColor(QPalette.PlaceholderText, QColor(theme.colors["text_muted"]))
        self.app.setPalette(pal)

    def _build_qss(self, theme: Theme) -> str:
        c = theme.colors
        return f"""
        QWidget {{
            background: {c['bg']};
            color: {c['text']};
            selection-background-color: {c['accent_soft']};
        }}
        QFrame#Toolbar {{
            background: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 6px;
        }}
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget, QTreeWidget {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 8px;
        }}
        QListWidget {{
            outline: none;
        }}
        QPushButton {{
            background: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 8px 12px;
        }}
        QPushButton:hover {{
            border-color: {c['accent']};
        }}
        QPushButton:pressed {{
            background: {c['bg_alt']};
        }}
        QPushButton[primary="true"] {{
            background: {c['accent']};
            color: {c['bg']};
            border: 1px solid {c['accent']};
        }}
        QListWidget::item {{
            padding: 7px 8px;
            margin: 2px 4px;
            border-radius: 6px;
            border: 1px solid transparent;
        }}
        QListWidget::item:hover {{
            background: {c['bg_alt']};
        }}
        QListWidget::item:focus {{
            outline: none;
        }}
        QListWidget::item:focus {{
            outline: none;
        }}
        QListWidget::item:selected {{
            background: {c['accent_soft']};
            color: {c['text']};
            border: 1px solid {c['accent']};
        }}
        QFrame[class="action-card"] {{
            background: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 10px;
        }}
        QLabel#ActionTitle {{
            font-size: 15px;
            font-weight: 600;
        }}
        QLabel#ActionDesc {{
            color: {c['text_muted']};
        }}
        QPlainTextEdit#LogPanel {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 8px;
        }}
        """
