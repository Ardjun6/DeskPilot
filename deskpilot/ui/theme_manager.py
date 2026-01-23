from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from PySide6.QtCore import QObject, Signal
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
            "bg": "#15171c",
            "bg_alt": "#1c2028",
            "surface": "#242a34",
            "surface_alt": "#1d222b",
            "border": "#353b46",
            "border_soft": "#2b313b",
            "text": "#f5f7fb",
            "text_muted": "#a7b0c2",
            "accent": "#6ea8ff",
            "accent_soft": "#2d3a52",
            "shadow": "#00000040",
            "input_bg": "#1f242c",
            "flow_start": "#2d3a52",
            "flow_end": "#40324a",
            "flow_step": "#273040",
            "flow_arrow": "#6ea8ff",
            "flow_text": "#f5f7fb",
            "flow_border": "#3a4250",
            "tag_blue": "#4f8cff",
            "tag_green": "#4ad6a7",
            "tag_orange": "#ffb454",
            "tag_red": "#ff6b6b",
            "tag_purple": "#b18aff",
            "tag_teal": "#4dd0e1",
            "tag_pink": "#ff7eb6",
            "tag_gray": "#93a0b5",
            "tag_text": "#0e1116",
        },
    ),
    "light": Theme(
        name="Light",
        is_dark=False,
        colors={
            "bg": "#f6f7fb",
            "bg_alt": "#eef1f6",
            "surface": "#ffffff",
            "surface_alt": "#f6f8fc",
            "border": "#d6dbe5",
            "border_soft": "#e4e9f3",
            "text": "#1f2430",
            "text_muted": "#6b7280",
            "accent": "#3f79ff",
            "accent_soft": "#e4ecff",
            "shadow": "#00000026",
            "input_bg": "#fdfdff",
            "flow_start": "#e4ecff",
            "flow_end": "#f3e8ff",
            "flow_step": "#f8f9fd",
            "flow_arrow": "#3f79ff",
            "flow_text": "#1f2430",
            "flow_border": "#d6dbe5",
            "tag_blue": "#2f6bff",
            "tag_green": "#12a87a",
            "tag_orange": "#f59f3a",
            "tag_red": "#e5484d",
            "tag_purple": "#8b5cf6",
            "tag_teal": "#119da4",
            "tag_pink": "#d946ef",
            "tag_gray": "#7b8798",
            "tag_text": "#ffffff",
        },
    ),
    "classic": Theme(
        name="Classic",
        is_dark=False,
        colors={
            "bg": "#e7eaef",
            "bg_alt": "#dfe3ea",
            "surface": "#f5f7fa",
            "surface_alt": "#edf1f6",
            "border": "#c6ccd8",
            "border_soft": "#d8dee8",
            "text": "#1f2430",
            "text_muted": "#555b66",
            "accent": "#416fb4",
            "accent_soft": "#d7e4f7",
            "shadow": "#00000020",
            "input_bg": "#ffffff",
            "flow_start": "#d7e4f7",
            "flow_end": "#e9dff8",
            "flow_step": "#f3f5fa",
            "flow_arrow": "#416fb4",
            "flow_text": "#1f2430",
            "flow_border": "#c6ccd8",
            "tag_blue": "#3a6bc4",
            "tag_green": "#2aa880",
            "tag_orange": "#e5962a",
            "tag_red": "#d44d4d",
            "tag_purple": "#8156d0",
            "tag_teal": "#198f97",
            "tag_pink": "#c548d8",
            "tag_gray": "#6f7a8a",
            "tag_text": "#ffffff",
        },
    ),
    "solarized": Theme(
        name="Solarized",
        is_dark=False,
        colors={
            "bg": "#fdf6e3",
            "bg_alt": "#eee8d5",
            "surface": "#fff9e8",
            "surface_alt": "#f3ebd6",
            "border": "#d9d1bb",
            "border_soft": "#e4dcc7",
            "text": "#2b333b",
            "text_muted": "#586e75",
            "accent": "#268bd2",
            "accent_soft": "#ddeaf6",
            "shadow": "#0000001f",
            "input_bg": "#fffaf0",
            "flow_start": "#ddeaf6",
            "flow_end": "#f2e2c4",
            "flow_step": "#fff7e2",
            "flow_arrow": "#268bd2",
            "flow_text": "#2b333b",
            "flow_border": "#d9d1bb",
            "tag_blue": "#268bd2",
            "tag_green": "#2aa198",
            "tag_orange": "#cb8b16",
            "tag_red": "#dc322f",
            "tag_purple": "#6c71c4",
            "tag_teal": "#268bd2",
            "tag_pink": "#d33682",
            "tag_gray": "#586e75",
            "tag_text": "#fffaf0",
        },
    ),
    "contrast": Theme(
        name="High Contrast",
        is_dark=True,
        colors={
            "bg": "#0b0b0b",
            "bg_alt": "#111111",
            "surface": "#141414",
            "surface_alt": "#1b1b1b",
            "border": "#2a2a2a",
            "border_soft": "#1f1f1f",
            "text": "#ffffff",
            "text_muted": "#c7c7c7",
            "accent": "#ffd400",
            "accent_soft": "#3a3200",
            "shadow": "#00000080",
            "input_bg": "#151515",
            "flow_start": "#2f2f2f",
            "flow_end": "#3a3200",
            "flow_step": "#1f1f1f",
            "flow_arrow": "#ffd400",
            "flow_text": "#ffffff",
            "flow_border": "#2a2a2a",
            "tag_blue": "#ffd400",
            "tag_green": "#00e5ff",
            "tag_orange": "#ff8c00",
            "tag_red": "#ff4d4f",
            "tag_purple": "#b48cff",
            "tag_teal": "#00bcd4",
            "tag_pink": "#ff6ac1",
            "tag_gray": "#b0b0b0",
            "tag_text": "#0b0b0b",
        },
    ),
}


class ThemeManager(QObject):
    """Central theme controller with runtime switching."""

    def __init__(self, app: QApplication, default: str = "dark") -> None:
        super().__init__()
        self.app = app
        self.current_key = default
        self.current = THEMES.get(default, list(THEMES.values())[0])
        self.apply(self.current, force=True)

    theme_changed = Signal(Theme)

    def set_theme(self, key: str) -> None:
        if key == "auto":
            palette = self.app.palette()
            is_dark = palette.window().color().value() < 128
            key = "dark" if is_dark else "light"
        theme = THEMES.get(key, self.current)
        self.current_key = key
        self.apply(theme, force=True)

    def apply(self, theme: Theme, *, force: bool = False) -> None:
        if not force and theme == self.current:
            return
        self.current = theme
        self._apply_palette(theme)
        self.app.setStyleSheet("")
        self.app.setStyleSheet(self._build_qss(theme))
        self.app.processEvents()
        self.theme_changed.emit(theme)

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
        pal.setColor(QPalette.Highlight, QColor(theme.colors["accent"]))
        pal.setColor(QPalette.HighlightedText, QColor(theme.colors["bg"]))
        self.app.setPalette(pal)

    def _build_qss(self, theme: Theme) -> str:
        c = theme.colors
        return f"""
        QWidget {{
            background: {c['bg']};
            color: {c['text']};
            selection-background-color: {c['accent_soft']};
            font-family: "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
        }}
        QMainWindow {{
            background: {c['bg']};
        }}
        QFrame {{
            background: transparent;
            border: none;
        }}
        QFrame#Toolbar {{
            background: {c['surface']};
            border: 1px solid {c['border_soft']};
            border-radius: 14px;
            padding: 10px;
        }}
        QDockWidget {{
            background: {c['surface']};
            border: none;
        }}
        QDockWidget::title {{
            background: transparent;
            padding: 0px;
        }}
        QListWidget#Sidebar {{
            background: {c['surface']};
            border: 1px solid {c['border_soft']};
            border-radius: 16px;
            padding: 8px;
        }}
        QListWidget#Sidebar::item {{
            padding: 10px 12px;
            margin: 3px 6px;
            border-radius: 10px;
        }}
        QListWidget#Sidebar::item:selected {{
            background: {c['accent_soft']};
            color: {c['text']};
        }}
        QListWidget#Sidebar::item:hover {{
            background: {c['bg_alt']};
        }}
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget, QTreeWidget, QTimeEdit, QSpinBox {{
            background: {c['input_bg']};
            border: 1px solid {c['border_soft']};
            border-radius: 10px;
            padding: 8px 10px;
        }}
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled, QComboBox:disabled, QListWidget:disabled,
        QTreeWidget:disabled, QTimeEdit:disabled, QSpinBox:disabled {{
            background: {c['surface_alt']};
            color: {c['text_muted']};
            border-color: {c['border_soft']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QTimeEdit:focus, QSpinBox:focus {{
            border-color: {c['accent']};
        }}
        QListWidget {{
            outline: none;
        }}
        QPushButton {{
            background: {c['surface']};
            border: 1px solid {c['border_soft']};
            border-radius: 10px;
            padding: 8px 14px;
        }}
        QPushButton:hover {{
            border-color: {c['accent']};
            background: {c['surface_alt']};
        }}
        QPushButton:pressed {{
            background: {c['accent_soft']};
        }}
        QPushButton[primary="true"] {{
            background: {c['accent']};
            color: {c['bg']};
            border: 1px solid {c['accent']};
        }}
        QPushButton[primary="true"]:hover {{
            background: {c['accent']};
            border-color: {c['accent']};
        }}
        QPushButton:disabled {{
            background: {c['surface_alt']};
            color: {c['text_muted']};
            border-color: {c['border_soft']};
        }}
        QFrame[card="true"] {{
            background: {c['surface']};
            border: 1px solid {c['border_soft']};
            border-radius: 14px;
        }}
        QFrame[action_card="true"][category="launch"] {{
            border-left: 4px solid {c['tag_blue']};
        }}
        QFrame[action_card="true"][category="template"] {{
            border-left: 4px solid {c['tag_purple']};
        }}
        QFrame[action_card="true"][category="flow"] {{
            border-left: 4px solid {c['tag_teal']};
        }}
        QFrame[action_card="true"][category="browser"] {{
            border-left: 4px solid {c['tag_orange']};
        }}
        QFrame[action_card="true"][category="utility"] {{
            border-left: 4px solid {c['tag_blue']};
        }}
        QFrame[action_card="true"][category="notes"] {{
            border-left: 4px solid {c['tag_purple']};
        }}
        QFrame[action_card="true"][category="email"] {{
            border-left: 4px solid {c['tag_purple']};
        }}
        QFrame[action_card="true"][category="productivity"] {{
            border-left: 4px solid {c['tag_green']};
        }}
        QFrame[action_card="true"][category="study"] {{
            border-left: 4px solid {c['tag_orange']};
        }}
        QFrame[action_card="true"][category="general"] {{
            border-left: 4px solid {c['tag_gray']};
        }}
        QFrame[class="grid-cell"] {{
            background: {c['surface']};
            border: 1px solid {c['border_soft']};
            border-radius: 16px;
        }}
        QLabel[chip="true"] {{
            background: {c['bg_alt']};
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 600;
            color: {c['tag_text']};
        }}
        QLabel[chip="true"][tag="launch"] {{
            background: {c['tag_blue']};
        }}
        QLabel[chip="true"][tag="template"],
        QLabel[chip="true"][tag="email"],
        QLabel[chip="true"][tag="notes"] {{
            background: {c['tag_purple']};
        }}
        QLabel[chip="true"][tag="flow"] {{
            background: {c['tag_teal']};
        }}
        QLabel[chip="true"][tag="work"],
        QLabel[chip="true"][tag="productivity"] {{
            background: {c['tag_green']};
        }}
        QLabel[chip="true"][tag="study"],
        QLabel[chip="true"][tag="browser"] {{
            background: {c['tag_orange']};
        }}
        QLabel[chip="true"][tag="utility"] {{
            background: {c['tag_blue']};
        }}
        QLabel[chip="true"][tag="safe"] {{
            background: {c['tag_green']};
        }}
        QLabel[chip="true"][tag="confirm"] {{
            background: {c['tag_orange']};
        }}
        QLabel[chip="true"][tag="danger"] {{
            background: {c['tag_red']};
        }}
        QLabel[chip="true"][tag="general"] {{
            background: {c['tag_gray']};
        }}
        QLabel#ActionTitle {{
            font-size: 15px;
            font-weight: 600;
        }}
        QLabel#ActionDesc {{
            color: {c['text_muted']};
        }}
        QLabel:disabled {{
            color: {c['text_muted']};
        }}
        QLabel#SectionTitle {{
            font-size: 14px;
            font-weight: 600;
        }}
        QPlainTextEdit#LogPanel {{
            background: {c['input_bg']};
            border: 1px solid {c['border_soft']};
            border-radius: 12px;
        }}
        QDialog#CommandPalette {{
            background: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 16px;
        }}
        QLineEdit#CommandPaletteInput {{
            background: {c['input_bg']};
            border: 1px solid {c['border_soft']};
            border-radius: 10px;
            padding: 10px;
        }}
        QListWidget#CommandPaletteList::item {{
            padding: 10px 12px;
            margin: 4px 6px;
            border-radius: 10px;
        }}
        QListWidget#CommandPaletteList::item:selected {{
            background: {c['accent_soft']};
        }}
        QListWidget#StepList::item {{
            padding: 8px 10px;
            margin: 4px 4px;
            border-radius: 10px;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 4px 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {c['border']};
            border-radius: 5px;
            min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {c['accent']};
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
            background: transparent;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
            margin: 2px 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {c['border']};
            border-radius: 5px;
            min-width: 24px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {c['accent']};
        }}
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
            background: transparent;
        }}
        """
