from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ActionCard(QFrame):
    """Individual action card with clean styling."""

    run_clicked = Signal(str)
    preview_clicked = Signal(str)
    context_menu_requested = Signal(str, object)

    def __init__(self, action: dict, parent=None) -> None:
        super().__init__(parent)
        self.action_id = action.get("id", "")
        self.is_enabled = action.get("enabled", True)
        self._setup_frame()
        self._build_content(action)

    def _setup_frame(self) -> None:
        self.setObjectName("ActionCard")
        self.setProperty("card", True)
        self.setProperty("action_card", True)
        self.setFrameShape(QFrame.NoFrame)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda pos: self.context_menu_requested.emit(self.action_id, self.mapToGlobal(pos))
        )

    def _build_content(self, action: dict) -> None:
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(16, 12, 16, 12)
        vbox.setSpacing(6)

        # Header row with title
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Title
        title = QLabel(action.get("name", "Untitled"))
        title.setObjectName("ActionTitle")
        header.addWidget(title)
        
        # Favorite star
        if action.get("favorite"):
            star = QLabel("⭐")
            star.setToolTip("Favorite")
            header.addWidget(star)
        
        header.addStretch()
        
        # Hotkey badge
        hotkey = action.get("hotkey")
        if hotkey:
            hotkey_label = QLabel(f"⌨ {hotkey}")
            hotkey_label.setObjectName("ActionDesc")
            header.addWidget(hotkey_label)
        
        vbox.addLayout(header)

        # Description
        desc_text = action.get("description", "")
        if desc_text:
            desc = QLabel(desc_text)
            desc.setObjectName("ActionDesc")
            desc.setWordWrap(True)
            vbox.addWidget(desc)

        # Tags row
        tag_row = self._build_tag_row(action)
        if tag_row is not None:
            vbox.addLayout(tag_row)

        vbox.addSpacing(4)

        # Action buttons
        hbox = QHBoxLayout()
        hbox.setSpacing(10)
        
        btn_run = QPushButton("▶ Run")
        btn_run.setProperty("primary", True)
        btn_run.setMinimumWidth(80)
        btn_run.clicked.connect(lambda: self.run_clicked.emit(self.action_id))
        
        btn_preview = QPushButton("👁 Preview")
        btn_preview.setMinimumWidth(90)
        btn_preview.clicked.connect(lambda: self.preview_clicked.emit(self.action_id))
        
        hbox.addWidget(btn_run)
        hbox.addWidget(btn_preview)
        hbox.addStretch()
        
        vbox.addLayout(hbox)

    def _build_tag_row(self, action: dict) -> QHBoxLayout | None:
        tags = action.get("tags") or []
        if not tags:
            return None
        row = QHBoxLayout()
        row.setSpacing(6)
        for tag in tags:
            label = QLabel(tag)
            label.setProperty("chip", True)
            label.setProperty("tag", str(tag).lower())
            row.addWidget(label)
        row.addStretch()
        return row


class ActionList(QWidget):
    """Scrollable list of action cards."""

    run_requested = Signal(str)
    preview_requested = Signal(str)
    edit_requested = Signal(str)
    delete_requested = Signal(str)
    hotkey_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._actions: List[dict] = []
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        self.layout.addStretch()

    def set_actions(self, actions: List[dict]) -> None:
        # Clear existing cards
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        self._actions = actions
        
        for action in actions:
            card = ActionCard(action)
            card.run_clicked.connect(self.run_requested.emit)
            card.preview_clicked.connect(self.preview_requested.emit)
            card.context_menu_requested.connect(self._open_context_menu)
            self.layout.insertWidget(self.layout.count() - 1, card)

    def _open_context_menu(self, action_id: str, pos) -> None:
        menu = QMenu(self)
        
        hotkey_action = menu.addAction("⌨ Set Hotkey")
        menu.addSeparator()
        edit_action = menu.addAction("✏ Edit")
        delete_action = menu.addAction("🗑 Delete")
        
        chosen = menu.exec(pos)
        if chosen == hotkey_action:
            self.hotkey_requested.emit(action_id)
        elif chosen == edit_action:
            self.edit_requested.emit(action_id)
        elif chosen == delete_action:
            self.delete_requested.emit(action_id)
