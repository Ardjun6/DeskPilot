from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QLineEdit, QListWidget, QListWidgetItem, 
    QVBoxLayout, QLabel, QHBoxLayout, QWidget
)


class CommandPalette(QDialog):
    """Centered modal command palette with keyboard navigation and fuzzy search."""

    action_chosen = Signal(str)  # action_id

    def __init__(self, parent=None, provider: Optional[Callable[[str], List[Tuple[str, str]]]] = None) -> None:
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setModal(True)
        self.setObjectName("CommandPalette")
        self.provider = provider or (lambda _text: [])
        self._last_query = ""

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header with title and keyboard hint
        header = QHBoxLayout()
        title = QLabel("⌘ Command Palette")
        title.setStyleSheet("font-size: 14px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        
        hint = QLabel("↑↓ navigate  •  ↵ select  •  esc close")
        hint.setObjectName("ActionDesc")
        hint.setStyleSheet("font-size: 11px;")
        header.addWidget(hint)
        layout.addLayout(header)

        # Search input
        self.edit = QLineEdit()
        self.edit.setObjectName("CommandPaletteInput")
        self.edit.setPlaceholderText("🔍 Type to search actions, macros, profiles...")
        layout.addWidget(self.edit)

        # Results list
        self.list = QListWidget()
        self.list.setObjectName("CommandPaletteList")
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.list, 1)

        # Footer with count
        self.footer = QLabel("")
        self.footer.setObjectName("ActionDesc")
        self.footer.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.footer)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self.edit.textChanged.connect(self._refresh)
        self.edit.returnPressed.connect(self._accept_current)
        self.list.itemActivated.connect(self._emit_selection)
        self.list.itemDoubleClicked.connect(self._emit_selection)
        self.edit.installEventFilter(self)

    def open_centered(self) -> None:
        self.resize(580, 450)
        if self.parent():
            geo = self.parent().geometry()
            self.move(geo.center().x() - self.width() // 2, geo.center().y() - self.height() // 2)
        self.edit.setText(self._last_query)
        self.edit.selectAll()
        self._refresh(self._last_query)
        self.show()
        self.edit.setFocus()

    def eventFilter(self, source, event) -> bool:  # noqa: N802 - Qt override signature
        if source is self.edit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.hide()
                return True
            if event.key() in (Qt.Key_Down, Qt.Key_Up):
                current = self.list.currentRow()
                if event.key() == Qt.Key_Down:
                    self.list.setCurrentRow(min(current + 1, self.list.count() - 1))
                else:
                    self.list.setCurrentRow(max(current - 1, 0))
                return True
            if event.key() == Qt.Key_Tab:
                # Tab to select and continue
                self._accept_current()
                return True
        return super().eventFilter(source, event)

    def _refresh(self, text: str) -> None:
        self._last_query = text or ""
        items = self.provider(self._last_query)
        self.list.clear()
        
        for action_id, label in items:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, action_id)
            self.list.addItem(item)
        
        if self.list.count() > 0:
            self.list.setCurrentRow(0)
        
        # Update footer
        count = self.list.count()
        if count == 0:
            self.footer.setText("No results found")
        elif count == 1:
            self.footer.setText("1 result")
        else:
            self.footer.setText(f"{count} results")

    def _accept_current(self) -> None:
        item = self.list.currentItem()
        if item:
            self._emit_selection(item)

    def _emit_selection(self, item: QListWidgetItem) -> None:
        action_id = item.data(Qt.UserRole)
        if action_id:
            self.action_chosen.emit(action_id)
        self.hide()
