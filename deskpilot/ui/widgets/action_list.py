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


class ActionList(QWidget):
    """List of action cards with run/preview controls."""

    run_requested = Signal(str)
    preview_requested = Signal(str)
    edit_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._actions: List[dict] = []
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        self.layout.addStretch()

    def set_actions(self, actions: List[dict]) -> None:
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._actions = actions
        for action in actions:
            self.layout.insertWidget(self.layout.count() - 1, self._build_card(action))

    def _build_card(self, action: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("ActionCard")
        card.setProperty("card", True)
        card.setProperty("action_card", True)
        card.setProperty("category", self._category_tag(action))
        card.setFrameShape(QFrame.NoFrame)
        card.setContextMenuPolicy(Qt.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos, i=action["id"], widget=card: self._open_context_menu(widget, pos, i)
        )
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(6)

        title = QLabel(action.get("name", "Untitled"))
        title.setObjectName("ActionTitle")
        desc = QLabel(action.get("description", ""))
        desc.setObjectName("ActionDesc")
        desc.setWordWrap(True)

        tag_row = self._build_tag_row(action)

        meta = QLabel(self._meta_text(action))
        meta.setObjectName("ActionDesc")

        hbox = QHBoxLayout()
        btn_run = QPushButton("Run")
        btn_run.setProperty("primary", True)
        btn_run.clicked.connect(lambda _checked=False, i=action["id"]: self.run_requested.emit(i))
        btn_preview = QPushButton("Preview")
        btn_preview.clicked.connect(lambda _checked=False, i=action["id"]: self.preview_requested.emit(i))
        hbox.addWidget(btn_run)
        hbox.addWidget(btn_preview)
        hbox.addStretch()

        vbox.addWidget(title)
        vbox.addWidget(desc)
        if tag_row is not None:
            vbox.addLayout(tag_row)
        vbox.addWidget(meta)
        vbox.addLayout(hbox)

        return card

    def _open_context_menu(self, widget: QWidget, pos, action_id: str) -> None:
        menu = QMenu(widget)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        chosen = menu.exec(widget.mapToGlobal(pos))
        if chosen == edit_action:
            self.edit_requested.emit(action_id)
        elif chosen == delete_action:
            self.delete_requested.emit(action_id)

    def _meta_text(self, action: dict) -> str:
        parts = []
        tags = action.get("tags") or []
        if tags:
            parts.append("Tags: " + ", ".join(tags))
        hotkey = action.get("hotkey")
        if hotkey:
            parts.append(f"Hotkey: {hotkey}")
        schedule_time = action.get("schedule_time")
        schedule_delay = action.get("schedule_delay")
        if schedule_time:
            parts.append(f"Schedule: {schedule_time}")
        elif schedule_delay:
            if schedule_delay >= 60:
                minutes = max(1, int(schedule_delay // 60))
                parts.append(f"Schedule: {minutes} min delay")
            else:
                parts.append(f"Schedule: {int(schedule_delay)} sec delay")
        app_title = action.get("app_title")
        if app_title:
            parts.append(f"App focus: {app_title}")
        return " | ".join(parts) if parts else ""

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

    def _category_tag(self, action: dict) -> str:
        tags = [str(tag).lower() for tag in (action.get("tags") or [])]
        for key in ("launch", "template", "flow", "browser", "utility", "notes", "email", "productivity", "study"):
            if key in tags:
                return key
        return tags[0] if tags else "general"
