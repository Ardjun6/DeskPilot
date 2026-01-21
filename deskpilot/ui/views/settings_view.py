from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ...config.config_manager import ConfigManager


class SettingsView(QWidget):
    """Placeholder settings view."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings view (to be implemented)"))
        self.setLayout(layout)

    def filter_items(self, text: str) -> None:
        _ = text
