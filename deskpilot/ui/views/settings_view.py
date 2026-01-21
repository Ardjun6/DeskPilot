from __future__ import annotations

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ...config.config_manager import ConfigManager


class SettingsView(QWidget):
    """Simple settings/info panel."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Config directory: {self.config_manager.config_dir}"))
        self.open_btn = QPushButton("Open config folder")
        self.open_btn.clicked.connect(self._open_folder)
        layout.addWidget(self.open_btn)
        layout.addStretch()
        self.setLayout(layout)

    def _open_folder(self) -> None:
        os.startfile(self.config_manager.config_dir)  # type: ignore[attr-defined]

    def filter_items(self, text: str) -> None:
        _ = text
