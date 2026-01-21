from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ...config.config_manager import ConfigManager


class TemplateView(QWidget):
    """Placeholder view for templates."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Template view (to be implemented)"))
        self.setLayout(layout)

    def filter_items(self, text: str) -> None:
        # TODO: apply filtering to template list
        _ = text
