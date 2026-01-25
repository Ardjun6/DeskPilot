"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         THEME MANAGER - STYLING CENTER                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎨 THIS IS WHERE YOU CHANGE ALL THE COLORS AND STYLING! 🎨                 ║
║                                                                              ║
║  HOW TO CUSTOMIZE:                                                           ║
║  ─────────────────                                                           ║
║  1. Find the theme you want to edit in the THEMES dictionary (line ~80)     ║
║  2. Change the color values (hex codes like "#ffffff")                       ║
║  3. Or create your own theme by copying an existing one                      ║
║                                                                              ║
║  COLOR MEANINGS:                                                             ║
║  ───────────────                                                             ║
║  • bg          = Main background color                                       ║
║  • bg_alt      = Alternate background (slightly different shade)             ║
║  • surface     = Card/panel backgrounds                                      ║
║  • border      = Border colors                                               ║
║  • text        = Main text color                                             ║
║  • text_muted  = Secondary/dimmed text                                       ║
║  • accent      = Primary accent color (buttons, highlights)                  ║
║  • accent_dark = Darker version of accent (hover states)                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtWidgets import QApplication


# ============================================================================
# THEME DATA CLASS
# ============================================================================
@dataclass(frozen=True)
class Theme:
    """
    Defines a complete UI theme.
    
    Attributes:
        name: Display name for the theme
        is_dark: True if this is a dark theme
        colors: Dictionary of color name -> hex code
        font_family: Font to use throughout the app
        font_size_base: Base font size in pixels
        border_radius: Roundness of corners in pixels
        spacing: Default spacing between elements
    """
    name: str
    is_dark: bool
    colors: Dict[str, str]
    font_family: str = "Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif"
    font_size_base: int = 13
    border_radius: int = 10
    spacing: int = 12


# ============================================================================
# ============================================================================
#
#                    🎨 THEME DEFINITIONS - EDIT COLORS HERE! 🎨
#
# ============================================================================
# ============================================================================

THEMES: Dict[str, Theme] = {
    
    # ========================================================================
    # THEME: CLEAN PRODUCTIVITY (Light)
    # ========================================================================
    # Modern, professional look with blue accents
    # Good for: Work environments, professional use
    # ========================================================================
    "productivity": Theme(
        name="Clean Productivity",
        is_dark=False,
        colors={
            # Background colors
            "bg": "#f8f9fc",              # Main background - light gray
            "bg_alt": "#f0f2f7",          # Alternate background
            
            # Surface colors (cards, panels)
            "surface": "#ffffff",          # Card backgrounds - white
            "surface_alt": "#f5f7fa",      # Alternate surface
            
            # Border colors
            "border": "#e2e6ef",           # Main borders
            "border_soft": "#eaeff7",      # Softer borders
            
            # Text colors
            "text": "#1a1f36",             # Main text - dark blue-gray
            "text_muted": "#6b7896",       # Secondary text - gray
            
            # Accent colors (buttons, highlights)
            "accent": "#4f6bed",           # Primary accent - blue
            "accent_soft": "#eef1fd",      # Light accent background
            "accent_dark": "#3d56c7",      # Dark accent for hover
            
            # Input fields
            "input_bg": "#ffffff",         # Input background
            
            # Flowchart colors
            "flow_start": "#eef1fd",
            "flow_end": "#f5f0fd",
            "flow_step": "#f8f9fc",
            "flow_arrow": "#4f6bed",
            "flow_text": "#1a1f36",
            "flow_border": "#e2e6ef",
            
            # Tag colors (for action tags)
            "tag_blue": "#4f6bed",
            "tag_green": "#22c55e",
            "tag_orange": "#f59e0b",
            "tag_red": "#ef4444",
            "tag_purple": "#a855f7",
            "tag_teal": "#14b8a6",
            "tag_pink": "#ec4899",
            "tag_gray": "#6b7896",
            "tag_text": "#ffffff",
            
            # Status colors
            "success": "#22c55e",           # Green
            "warning": "#f59e0b",           # Orange
            "error": "#ef4444",             # Red
            
            # Misc
            "shadow": "#1a1f3610",
        },
        font_family="Inter, Segoe UI, -apple-system, sans-serif",
        font_size_base=13,
        border_radius=10,
    ),

    # ========================================================================
    # THEME: CALM FOCUS (Light)
    # ========================================================================
    # Soft, warm colors that are easy on the eyes
    # Good for: Long sessions, reduced eye strain
    # ========================================================================
    "calm": Theme(
        name="Calm Focus",
        is_dark=False,
        colors={
            # Background colors - warm off-white
            "bg": "#faf8f5",
            "bg_alt": "#f3f0eb",
            
            # Surface colors
            "surface": "#fffefa",
            "surface_alt": "#f8f5f0",
            
            # Border colors - warm gray
            "border": "#e5ddd2",
            "border_soft": "#ede7df",
            
            # Text colors
            "text": "#3d3833",
            "text_muted": "#8a8279",
            
            # Accent colors - soft green
            "accent": "#7c9a72",
            "accent_soft": "#e8f0e5",
            "accent_dark": "#5d7a55",
            
            # Input fields
            "input_bg": "#fffefa",
            
            # Flowchart colors
            "flow_start": "#e8f0e5",
            "flow_end": "#f5ede5",
            "flow_step": "#faf8f5",
            "flow_arrow": "#7c9a72",
            "flow_text": "#3d3833",
            "flow_border": "#e5ddd2",
            
            # Tag colors
            "tag_blue": "#6b8fc7",
            "tag_green": "#7c9a72",
            "tag_orange": "#c7945d",
            "tag_red": "#c77272",
            "tag_purple": "#9a7cb3",
            "tag_teal": "#6ba3a0",
            "tag_pink": "#c77ca0",
            "tag_gray": "#8a8279",
            "tag_text": "#fffefa",
            
            # Status colors
            "success": "#7c9a72",
            "warning": "#c7945d",
            "error": "#c77272",
            
            # Misc
            "shadow": "#3d383308",
        },
        font_family="Georgia, Segoe UI, serif",
        font_size_base=13,
        border_radius=8,
    ),

    # ========================================================================
    # THEME: HIGH CONTRAST (Dark)
    # ========================================================================
    # Maximum readability with strong contrast
    # Good for: Accessibility, visibility in bright environments
    # ========================================================================
    "contrast": Theme(
        name="High Contrast",
        is_dark=True,
        colors={
            # Background colors - pure black
            "bg": "#000000",
            "bg_alt": "#0a0a0a",
            
            # Surface colors - very dark
            "surface": "#111111",
            "surface_alt": "#1a1a1a",
            
            # Border colors - visible gray
            "border": "#444444",
            "border_soft": "#333333",
            
            # Text colors - high contrast
            "text": "#ffffff",
            "text_muted": "#aaaaaa",
            
            # Accent colors - bright yellow
            "accent": "#ffdd00",
            "accent_soft": "#2a2800",
            "accent_dark": "#ccb000",
            
            # Input fields
            "input_bg": "#111111",
            
            # Flowchart colors
            "flow_start": "#1a2a1a",
            "flow_end": "#2a1a1a",
            "flow_step": "#1a1a1a",
            "flow_arrow": "#ffdd00",
            "flow_text": "#ffffff",
            "flow_border": "#444444",
            
            # Tag colors - bright versions
            "tag_blue": "#66aaff",
            "tag_green": "#44ff88",
            "tag_orange": "#ffaa44",
            "tag_red": "#ff6666",
            "tag_purple": "#cc88ff",
            "tag_teal": "#44ffdd",
            "tag_pink": "#ff88cc",
            "tag_gray": "#aaaaaa",
            "tag_text": "#000000",
            
            # Status colors
            "success": "#44ff88",
            "warning": "#ffdd00",
            "error": "#ff6666",
            
            # Misc
            "shadow": "#00000080",
        },
        font_family="Consolas, Segoe UI, monospace",
        font_size_base=14,
        border_radius=4,
    ),

    # ========================================================================
    # THEME: PLAYFUL (Dark)
    # ========================================================================
    # Fun, vibrant colors with purple/pink accents
    # Good for: Personal use, creative work
    # ========================================================================
    "playful": Theme(
        name="Playful",
        is_dark=True,
        colors={
            # Background colors - dark purple
            "bg": "#1a1625",
            "bg_alt": "#221d2e",
            
            # Surface colors
            "surface": "#2a2438",
            "surface_alt": "#322b42",
            
            # Border colors
            "border": "#3d3552",
            "border_soft": "#352f48",
            
            # Text colors
            "text": "#f0e6ff",
            "text_muted": "#9d8fba",
            
            # Accent colors - vibrant pink/purple
            "accent": "#e879f9",
            "accent_soft": "#3d2545",
            "accent_dark": "#c026d3",
            
            # Input fields
            "input_bg": "#221d2e",
            
            # Flowchart colors
            "flow_start": "#2d3548",
            "flow_end": "#3d2545",
            "flow_step": "#2a2438",
            "flow_arrow": "#e879f9",
            "flow_text": "#f0e6ff",
            "flow_border": "#3d3552",
            
            # Tag colors - vibrant
            "tag_blue": "#60a5fa",
            "tag_green": "#4ade80",
            "tag_orange": "#fb923c",
            "tag_red": "#f87171",
            "tag_purple": "#e879f9",
            "tag_teal": "#2dd4bf",
            "tag_pink": "#f472b6",
            "tag_gray": "#9d8fba",
            "tag_text": "#1a1625",
            
            # Status colors
            "success": "#4ade80",
            "warning": "#fbbf24",
            "error": "#f87171",
            
            # Misc
            "shadow": "#0d0a1240",
        },
        font_family="Segoe UI, -apple-system, sans-serif",
        font_size_base=13,
        border_radius=12,
    ),

    # ========================================================================
    # THEME: MODERN GLASS (Dark) - DEFAULT
    # ========================================================================
    # Sleek, modern dark theme with subtle transparency effects
    # Good for: Modern look, daily use
    # ========================================================================
    "glass": Theme(
        name="Modern Glass",
        is_dark=True,
        colors={
            # Background colors - dark blue-gray
            "bg": "#0f1419",              # Main background
            "bg_alt": "#151b23",          # Slightly lighter
            
            # Surface colors - card backgrounds
            "surface": "#1a212b",         # Card background
            "surface_alt": "#1f2733",     # Alternate surface
            
            # Border colors
            "border": "#2d3848",          # Main borders
            "border_soft": "#252d3a",     # Softer borders
            
            # Text colors
            "text": "#e6edf5",            # Main text - off-white
            "text_muted": "#7d8a9a",      # Secondary text - gray
            
            # Accent colors - cyan/teal
            "accent": "#3b9eff",          # Primary accent - bright blue
            "accent_soft": "#1a2d42",     # Light accent background
            "accent_dark": "#2d7fd4",     # Dark accent for hover
            
            # Input fields
            "input_bg": "#151b23",        # Input background
            
            # Flowchart colors
            "flow_start": "#1a3028",
            "flow_end": "#2a1f2a",
            "flow_step": "#1a212b",
            "flow_arrow": "#3b9eff",
            "flow_text": "#e6edf5",
            "flow_border": "#2d3848",
            
            # Tag colors
            "tag_blue": "#3b9eff",
            "tag_green": "#34d399",
            "tag_orange": "#fbbf24",
            "tag_red": "#f87171",
            "tag_purple": "#a78bfa",
            "tag_teal": "#2dd4bf",
            "tag_pink": "#f472b6",
            "tag_gray": "#7d8a9a",
            "tag_text": "#0f1419",
            
            # Status colors
            "success": "#34d399",         # Green
            "warning": "#fbbf24",         # Yellow
            "error": "#f87171",           # Red
            
            # Misc
            "shadow": "#00000040",
        },
        font_family="Segoe UI, -apple-system, BlinkMacSystemFont, sans-serif",
        font_size_base=13,
        border_radius=10,
    ),
}


# ============================================================================
# THEME MANAGER CLASS
# ============================================================================
class ThemeManager(QObject):
    """
    Manages application theming.
    
    This class:
    - Stores the current theme
    - Applies styles to the entire application
    - Emits signals when theme changes
    
    Usage:
        manager = ThemeManager()
        manager.set_theme("glass")
        colors = manager.current.colors
    """
    
    # Signal emitted when theme changes
    theme_changed = Signal(Theme)
    
    def __init__(self) -> None:
        super().__init__()
        # Default to glass theme
        self._current_theme = THEMES["glass"]
        self._current_key = "glass"
    
    @property
    def current(self) -> Theme:
        """Get the currently active theme."""
        return self._current_theme
    
    @property
    def current_key(self) -> str:
        """Get the key of the current theme."""
        return self._current_key
    
    @property
    def available_themes(self) -> list[str]:
        """Get list of available theme names."""
        return list(THEMES.keys())
    
    def get_theme_display_names(self) -> list[tuple[str, str]]:
        """Get list of (key, display_name) tuples for all themes."""
        return [(key, theme.name) for key, theme in THEMES.items()]
    
    def set_theme(self, theme_name: str) -> None:
        """
        Change the current theme.
        
        Args:
            theme_name: Name of theme to activate (e.g., "glass", "productivity")
        """
        if theme_name not in THEMES:
            print(f"Warning: Unknown theme '{theme_name}', using 'glass'")
            theme_name = "glass"
        
        self._current_key = theme_name
        self._current_theme = THEMES[theme_name]
        self._apply_theme()
        self.theme_changed.emit(self._current_theme)
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the application."""
        app = QApplication.instance()
        if app is None:
            return
        
        theme = self._current_theme
        colors = theme.colors
        
        # Build the stylesheet
        stylesheet = self._build_stylesheet(theme)
        app.setStyleSheet(stylesheet)
        
        # Set palette for native widgets
        palette = self._build_palette(colors)
        app.setPalette(palette)
        
        # Set font
        font = QFont(theme.font_family.split(",")[0].strip())
        font.setPointSize(theme.font_size_base)
        app.setFont(font)
    
    def _build_palette(self, colors: Dict[str, str]) -> QPalette:
        """Build a QPalette from theme colors."""
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor(colors["bg"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text"]))
        
        # Base colors (for inputs, lists)
        palette.setColor(QPalette.Base, QColor(colors["surface"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["surface_alt"]))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.PlaceholderText, QColor(colors["text_muted"]))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(colors["surface"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["text"]))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(colors["accent"]))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        
        return palette
    
    def _build_stylesheet(self, theme: Theme) -> str:
        """
        Build the complete application stylesheet.
        
        This is where all the CSS-like styling is defined.
        Edit this method to change how widgets look!
        """
        c = theme.colors  # Shorthand
        r = theme.border_radius
        
        return f"""
            /* ============================================================
               GLOBAL STYLES
               ============================================================ */
            
            QWidget {{
                background-color: {c['bg']};
                color: {c['text']};
                font-family: {theme.font_family};
                font-size: {theme.font_size_base}px;
            }}
            
            /* ============================================================
               MAIN WINDOW
               ============================================================ */
            
            QMainWindow {{
                background-color: {c['bg']};
            }}
            
            /* ============================================================
               BUTTONS
               ============================================================ */
            
            QPushButton {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                padding: 8px 16px;
                color: {c['text']};
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {c['bg_alt']};
                border-color: {c['accent']};
            }}
            
            QPushButton:pressed {{
                background-color: {c['accent']};
                color: white;
            }}
            
            QPushButton:disabled {{
                background-color: {c['bg_alt']};
                color: {c['text_muted']};
            }}
            
            /* Primary buttons (property: primary=true) */
            QPushButton[primary="true"] {{
                background-color: {c['accent']};
                color: white;
                border: none;
            }}
            
            QPushButton[primary="true"]:hover {{
                background-color: {c['accent_dark']};
            }}
            
            /* ============================================================
               INPUT FIELDS
               ============================================================ */
            
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                padding: 8px 12px;
                color: {c['text']};
                selection-background-color: {c['accent']};
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {c['accent']};
            }}
            
            /* ============================================================
               DROPDOWNS / COMBO BOX
               ============================================================ */
            
            QComboBox {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                padding: 8px 12px;
                color: {c['text']};
                min-width: 100px;
            }}
            
            QComboBox:hover {{
                border-color: {c['accent']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                selection-background-color: {c['accent']};
                padding: 4px;
            }}
            
            /* ============================================================
               SPIN BOXES (Number inputs)
               ============================================================ */
            
            QSpinBox, QDoubleSpinBox {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                padding: 6px 10px;
                color: {c['text']};
            }}
            
            /* ============================================================
               CHECKBOXES
               ============================================================ */
            
            QCheckBox {{
                color: {c['text']};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {c['border']};
                background-color: {c['input_bg']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {c['accent']};
                border-color: {c['accent']};
            }}
            
            /* ============================================================
               SCROLL BARS
               ============================================================ */
            
            QScrollBar:vertical {{
                background-color: {c['bg']};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {c['border']};
                border-radius: 5px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {c['text_muted']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            QScrollBar:horizontal {{
                background-color: {c['bg']};
                height: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {c['border']};
                border-radius: 5px;
                min-width: 30px;
            }}
            
            /* ============================================================
               SCROLL AREAS
               ============================================================ */
            
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            
            /* ============================================================
               LISTS
               ============================================================ */
            
            QListWidget {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                padding: 4px;
                outline: none;
            }}
            
            QListWidget::item {{
                padding: 10px 14px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            QListWidget::item:selected {{
                background-color: {c['accent']};
                color: white;
            }}
            
            QListWidget::item:hover:!selected {{
                background-color: {c['bg_alt']};
            }}
            
            /* ============================================================
               LABELS
               ============================================================ */
            
            QLabel {{
                color: {c['text']};
                background: transparent;
            }}
            
            /* ============================================================
               FRAMES (Cards, Panels)
               ============================================================ */
            
            QFrame {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
            }}
            
            /* ============================================================
               MENUS
               ============================================================ */
            
            QMenu {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {c['accent']};
                color: white;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {c['border']};
                margin: 4px 8px;
            }}
            
            /* ============================================================
               TOOLTIPS
               ============================================================ */
            
            QToolTip {{
                background-color: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px 10px;
            }}
            
            /* ============================================================
               PROGRESS BARS
               ============================================================ */
            
            QProgressBar {{
                background-color: {c['bg_alt']};
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {c['accent']};
                border-radius: 4px;
            }}
            
            /* ============================================================
               SPLITTERS
               ============================================================ */
            
            QSplitter::handle {{
                background-color: {c['border']};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
            
            /* ============================================================
               TIME EDIT
               ============================================================ */
            
            QTimeEdit {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: {r}px;
                padding: 6px 10px;
                color: {c['text']};
            }}
        """
    
    def get_color(self, color_name: str) -> str:
        """
        Get a specific color from the current theme.
        
        Args:
            color_name: Name of the color (e.g., "accent", "text")
            
        Returns:
            Hex color code
        """
        return self._current_theme.colors.get(color_name, "#ffffff")
