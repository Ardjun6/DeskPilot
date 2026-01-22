from __future__ import annotations

import os
from typing import Optional

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ...config.config_manager import ConfigManager
from ..widgets.grid_layout import GridCanvas


class SettingsView(QWidget):
    """Simple settings/info panel."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        grid = GridCanvas()
        info_cell = grid.add_cell(0, 0, row_span=3, col_span=2, title="Settings")
        info_cell.layout.addWidget(QLabel(f"Config directory: {self.config_manager.config_dir}"))
        self.open_btn = QPushButton("Open config folder")
        self.open_btn.clicked.connect(self._open_folder)
        info_cell.layout.addWidget(self.open_btn)
        info_cell.layout.addStretch()

        tips_cell = grid.add_cell(0, 2, row_span=3, col_span=1, title="Tips")
        tip_theme = QLabel("Themes, navigation position, and shortcuts apply immediately.")
        tip_theme.setObjectName("ActionDesc")
        tip_profiles = QLabel("Use profiles to launch app bundles quickly.")
        tip_profiles.setObjectName("ActionDesc")
        tips_cell.layout.addWidget(tip_theme)
        tips_cell.layout.addWidget(tip_profiles)
        tips_cell.layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(grid)
        self.setLayout(layout)

    def _open_folder(self) -> None:
        os.startfile(self.config_manager.config_dir)  # type: ignore[attr-defined]

    def filter_items(self, text: str) -> None:
        _ = text
