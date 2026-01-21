from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from ...utils.app_discovery import DiscoveredApp, discover_apps


class AppPickerDialog(QDialog):
    def __init__(self, parent=None, apps: Optional[List[DiscoveredApp]] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pick application")
        self.apps = apps or discover_apps()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search apps...")
        self.list_widget = QListWidget()
        self.rescan = QPushButton("Rescan")

        hl = QHBoxLayout()
        hl.addWidget(self.search)
        hl.addWidget(self.rescan)

        layout = QVBoxLayout(self)
        layout.addLayout(hl)
        layout.addWidget(self.list_widget)

        self.search.textChanged.connect(self._filter)
        self.rescan.clicked.connect(self._rescan)
        self.list_widget.itemDoubleClicked.connect(lambda _: self.accept())

        self._populate(self.apps)

    def _populate(self, apps: List[DiscoveredApp]) -> None:
        self.list_widget.clear()
        for app in apps:
            item = QListWidgetItem(app.name)
            item.setData(Qt.UserRole, app.path)
            item.setToolTip(app.path)
            item.setIcon(QIcon(app.path))
            self.list_widget.addItem(item)

    def _filter(self, text: str) -> None:
        term = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            visible = term in item.text().lower() or term in (item.toolTip() or "").lower()
            item.setHidden(not visible)

    def _rescan(self) -> None:
        self.apps = discover_apps()
        self._populate(self.apps)

    def selected_path(self) -> Optional[str]:
        item = self.list_widget.currentItem()
        if item:
            return item.data(Qt.UserRole)
        return None
