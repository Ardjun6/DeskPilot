from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ...config.config_manager import ConfigManager


class LaunchView(QWidget):
    """Placeholder view for launch profiles."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Launch view (to be implemented)"))
        self.setLayout(layout)

    def filter_items(self, text: str) -> None:
        _ = text
