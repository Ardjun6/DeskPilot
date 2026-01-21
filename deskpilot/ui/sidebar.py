from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QStyle


class Sidebar(QListWidget):
    """Simple sidebar list for navigation."""

    section_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._populate()
        self.currentRowChanged.connect(self.section_changed.emit)

    def _populate(self) -> None:
        icons = [
            QStyle.SP_ComputerIcon,
            QStyle.SP_FileIcon,
            QStyle.SP_MediaPlay,
            QStyle.SP_DirOpenIcon,
            QStyle.SP_DesktopIcon,
            QStyle.SP_FileDialogDetailedView,
        ]
        for label, icon in zip(
            ["Actions", "Templates", "Macros", "Flows", "Launchers", "Settings"],
            icons,
        ):
            item = QListWidgetItem(self.style().standardIcon(icon), label)
            self.addItem(item)
        self.setCurrentRow(0)
