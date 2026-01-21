from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from ...actions.engine import ActionEngine
from ...config.config_manager import ConfigManager
from ..widgets.action_list import ActionList


class ActionView(QWidget):
    """Action list view with run/preview signals."""

    def __init__(
        self,
        config_manager: ConfigManager,
        action_engine: ActionEngine,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.action_engine = action_engine

        self.list_widget = ActionList()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(4, 4, 4, 4)
        container_layout.addWidget(self.list_widget)
        scroll.setWidget(container)

        self.empty = QLabel("No actions found. Add entries to actions.yaml.")
        self.empty.setObjectName("ActionDesc")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.list_widget.run_requested.connect(self._emit_run)
        self.list_widget.preview_requested.connect(self._emit_preview)

        self.refresh()

    def refresh(self) -> None:
        actions = [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "favorite": a.favorite,
                "tags": a.tags,
                "hotkey": a.hotkey,
            }
            for a in self.action_engine.list_actions()
        ]
        if not actions:
            self.list_widget.hide()
            if self.empty.parent() is None:
                self.layout().addWidget(self.empty)
            self.empty.show()
        else:
            self.empty.hide()
            self.list_widget.show()
            self.list_widget.set_actions(actions)

    def filter_items(self, text: str) -> None:
        text_lower = text.lower()
        filtered = [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "favorite": a.favorite,
                "tags": a.tags,
                "hotkey": a.hotkey,
            }
            for a in self.action_engine.list_actions()
            if text_lower in a.name.lower()
            or text_lower in a.description.lower()
            or any(text_lower in t.lower() for t in a.tags)
        ]
        self.list_widget.set_actions(filtered)

    # Signals are proxied via parent MainWindow using Qt's signal/slot;
    # we keep these as simple passthrough hooks.
    def _emit_run(self, action_id: str) -> None:
        self.parent().run_action(action_id)  # type: ignore[attr-defined]

    def _emit_preview(self, action_id: str) -> None:
        self.parent().preview_action(action_id)  # type: ignore[attr-defined]
