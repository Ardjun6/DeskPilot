from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout


class CommandPalette(QDialog):
    """Centered modal command palette with keyboard navigation."""

    action_chosen = Signal(str)  # action_id

    def __init__(self, parent=None, provider: Optional[Callable[[str], List[Tuple[str, str]]]] = None) -> None:
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setModal(True)
        self.provider = provider or (lambda _text: [])

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Type to search actions...")
        self.list = QListWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(self.edit)
        layout.addWidget(self.list)
        self.setLayout(layout)

        self.edit.textChanged.connect(self._refresh)
        self.edit.returnPressed.connect(self._accept_current)
        self.list.itemActivated.connect(self._emit_selection)

    def open_centered(self) -> None:
        self.resize(540, 420)
        if self.parent():
            geo = self.parent().geometry()
            self.move(geo.center().x() - self.width() // 2, geo.center().y() - self.height() // 2)
        self._refresh("")
        self.show()
        self.edit.setFocus()

    def _refresh(self, text: str) -> None:
        items = self.provider(text or "")
        self.list.clear()
        for action_id, label in items:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, action_id)
            self.list.addItem(item)
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _accept_current(self) -> None:
        item = self.list.currentItem()
        if item:
            self._emit_selection(item)

    def _emit_selection(self, item: QListWidgetItem) -> None:
        action_id = item.data(Qt.UserRole)
        if action_id:
            self.action_chosen.emit(action_id)
        self.hide()
