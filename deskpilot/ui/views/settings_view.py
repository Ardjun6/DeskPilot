from __future__ import annotations

import os
import platform
from typing import Optional

from PySide6.QtWidgets import (
    QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QFrame
)

from ...config.config_manager import ConfigManager
from ..widgets.grid_layout import GridCanvas


class SettingsView(QWidget):
    """Settings and information panel with theme info and config access."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self._build_ui()

    def _build_ui(self) -> None:
        grid = GridCanvas()
        
        # Main settings cell
        settings_cell = grid.add_cell(0, 0, row_span=2, col_span=2, title="⚙️ Settings")
        
        # Config directory
        config_label = QLabel(f"📁 Config directory:")
        config_label.setObjectName("ActionDesc")
        settings_cell.layout.addWidget(config_label)
        
        config_path = QLabel(f"{self.config_manager.config_dir}")
        config_path.setWordWrap(True)
        config_path.setStyleSheet("font-family: monospace; font-size: 11px; padding: 8px; background: palette(base); border-radius: 6px;")
        settings_cell.layout.addWidget(config_path)
        
        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        self.open_btn = QPushButton("📂 Open Config Folder")
        self.open_btn.clicked.connect(self._open_folder)
        btn_row.addWidget(self.open_btn)
        
        self.reload_btn = QPushButton("🔄 Reload Config")
        self.reload_btn.clicked.connect(self._reload_config)
        btn_row.addWidget(self.reload_btn)
        
        btn_row.addStretch()
        settings_cell.layout.addLayout(btn_row)
        
        settings_cell.layout.addSpacing(16)
        
        # System info
        sys_label = QLabel("💻 System Information")
        sys_label.setObjectName("SectionTitle")
        settings_cell.layout.addWidget(sys_label)
        
        sys_info = QLabel(
            f"Platform: {platform.system()} {platform.release()}\n"
            f"Python: {platform.python_version()}"
        )
        sys_info.setObjectName("ActionDesc")
        settings_cell.layout.addWidget(sys_info)
        
        settings_cell.layout.addStretch()

        # Tips and shortcuts cell
        tips_cell = grid.add_cell(0, 2, row_span=1, col_span=1, title="💡 Tips")
        
        tips = [
            "🎨 Themes apply instantly - try them all!",
            "⌨️ Use Ctrl+K to open command palette",
            "🔧 Right-click items for more options",
            "📌 Set hotkeys for quick access",
            "⏰ Schedule macros with delays or times",
        ]
        
        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setObjectName("ActionDesc")
            tip_label.setWordWrap(True)
            tips_cell.layout.addWidget(tip_label)
        
        tips_cell.layout.addStretch()

        # Keyboard shortcuts cell
        shortcuts_cell = grid.add_cell(1, 2, row_span=1, col_span=1, title="⌨️ Shortcuts")
        
        shortcuts = [
            ("Ctrl+K", "Command palette"),
            ("Ctrl+R", "Run selected"),
            ("Ctrl+P", "Preview selected"),
            ("Escape", "Close dialogs"),
        ]
        
        for key, desc in shortcuts:
            shortcut_row = QHBoxLayout()
            key_label = QLabel(key)
            key_label.setStyleSheet(
                "background: palette(button); padding: 3px 8px; border-radius: 4px; "
                "font-family: monospace; font-size: 11px; font-weight: 600;"
            )
            key_label.setFixedWidth(70)
            shortcut_row.addWidget(key_label)
            
            desc_label = QLabel(desc)
            desc_label.setObjectName("ActionDesc")
            shortcut_row.addWidget(desc_label)
            shortcut_row.addStretch()
            
            shortcuts_cell.layout.addLayout(shortcut_row)
        
        shortcuts_cell.layout.addStretch()

        # About cell
        about_cell = grid.add_cell(2, 0, row_span=1, col_span=3, title="ℹ️ About DeskPilot")
        
        about_text = QLabel(
            "DeskPilot is your desktop automation copilot. "
            "Create actions, schedule macros, build templates, and launch apps with ease. "
            "All your automation needs in one friendly interface."
        )
        about_text.setObjectName("ActionDesc")
        about_text.setWordWrap(True)
        about_cell.layout.addWidget(about_text)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setObjectName("ActionDesc")
        version_label.setStyleSheet("font-size: 11px; opacity: 0.7;")
        about_cell.layout.addWidget(version_label)
        
        about_cell.layout.addStretch()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(grid)
        self.setLayout(layout)

    def _open_folder(self) -> None:
        path = str(self.config_manager.config_dir)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

    def _reload_config(self) -> None:
        self.config_manager.ensure_loaded()
        # Notify main window to refresh
        main = self.window()
        if hasattr(main, "refresh_hotkeys"):
            main.refresh_hotkeys()

    def filter_items(self, text: str) -> None:
        _ = text
