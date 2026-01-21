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
            "bg": "#15171c",
            "bg_alt": "#1c2028",
            "surface": "#242a34",
            "border": "#353b46",
            "text": "#f5f7fb",
            "text_muted": "#a7b0c2",
            "accent": "#6ea8ff",
            "accent_soft": "#2d3a52",
            "shadow": "#00000040",
            "input_bg": "#1f242c",
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
            "border": "#d6dbe5",
            "text": "#1f2430",
            "text_muted": "#6b7280",
            "accent": "#3f79ff",
            "accent_soft": "#e4ecff",
            "shadow": "#00000026",
            "input_bg": "#fdfdff",
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
            "border": "#c6ccd8",
            "text": "#1f2430",
            "text_muted": "#555b66",
            "accent": "#416fb4",
            "accent_soft": "#d7e4f7",
            "shadow": "#00000020",
            "input_bg": "#ffffff",
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
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {c['surface']}, stop:1 {c['bg_alt']});
            border: 1px solid {c['border']};
            border-radius: 10px;
            padding: 8px;
        }}
        QListWidget#Sidebar {{
            background: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 6px;
        }}
        QListWidget#Sidebar::item {{
            padding: 8px 10px;
            margin: 3px 4px;
            border-radius: 8px;
        }}
        QListWidget#Sidebar::item:selected {{
            background: {c['accent_soft']};
            color: {c['text']};
            border: 1px solid {c['accent']};
        }}
        QListWidget#Sidebar::item:hover {{
            background: {c['bg_alt']};
        }}
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget, QTreeWidget {{
            background: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 10px;
            padding: 9px 10px;
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
            border-color: {c['accent']};
        }}
        QListWidget {{
            outline: none;
        }}
        QPushButton {{
            background: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 10px;
            padding: 8px 14px;
        }}
        QPushButton:hover {{
            border-color: {c['accent']};
            background: {c['bg_alt']};
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
        QListWidget::item {{
            padding: 8px 10px;
            margin: 3px 6px;
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
            border-radius: 12px;
        }}
        QFrame[class="action-card"][category="launch"] {{
            border-left: 4px solid {c['tag_blue']};
        }}
        QFrame[class="action-card"][category="template"] {{
            border-left: 4px solid {c['tag_purple']};
        }}
        QFrame[class="action-card"][category="flow"] {{
            border-left: 4px solid {c['tag_teal']};
        }}
        QFrame[class="action-card"][category="browser"] {{
            border-left: 4px solid {c['tag_orange']};
        }}
        QFrame[class="action-card"][category="utility"] {{
            border-left: 4px solid {c['tag_blue']};
        }}
        QFrame[class="action-card"][category="notes"] {{
            border-left: 4px solid {c['tag_purple']};
        }}
        QFrame[class="action-card"][category="email"] {{
            border-left: 4px solid {c['tag_purple']};
        }}
        QFrame[class="action-card"][category="productivity"] {{
            border-left: 4px solid {c['tag_green']};
        }}
        QFrame[class="action-card"][category="study"] {{
            border-left: 4px solid {c['tag_orange']};
        }}
        QFrame[class="action-card"][category="general"] {{
            border-left: 4px solid {c['tag_gray']};
        }}
        QLabel[class="tag-chip"] {{
            background: {c['bg_alt']};
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 600;
            color: {c['tag_text']};
        }}
        QLabel[class="tag-chip"][tag="launch"] {{
            background: {c['tag_blue']};
        }}
        QLabel[class="tag-chip"][tag="template"],
        QLabel[class="tag-chip"][tag="email"],
        QLabel[class="tag-chip"][tag="notes"] {{
            background: {c['tag_purple']};
        }}
        QLabel[class="tag-chip"][tag="flow"] {{
            background: {c['tag_teal']};
        }}
        QLabel[class="tag-chip"][tag="work"],
        QLabel[class="tag-chip"][tag="productivity"] {{
            background: {c['tag_green']};
        }}
        QLabel[class="tag-chip"][tag="study"],
        QLabel[class="tag-chip"][tag="browser"] {{
            background: {c['tag_orange']};
        }}
        QLabel[class="tag-chip"][tag="utility"] {{
            background: {c['tag_blue']};
        }}
        QLabel[class="tag-chip"][tag="safe"] {{
            background: {c['tag_green']};
        }}
        QLabel[class="tag-chip"][tag="confirm"] {{
            background: {c['tag_orange']};
        }}
        QLabel[class="tag-chip"][tag="danger"] {{
            background: {c['tag_red']};
        }}
        QLabel[class="tag-chip"][tag="general"] {{
            background: {c['tag_gray']};
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
