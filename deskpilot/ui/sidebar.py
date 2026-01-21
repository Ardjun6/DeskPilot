from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget


class Sidebar(QListWidget):
    """Simple sidebar list for navigation."""

    section_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._populate()
        self.currentRowChanged.connect(self.section_changed.emit)

    def _populate(self) -> None:
        for label in ["Templates", "Macros", "Flows", "Launchers", "Settings"]:
            item = QListWidgetItem(label)
            self.addItem(item)
        self.setCurrentRow(0)
