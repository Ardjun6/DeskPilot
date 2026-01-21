from __future__ import annotations

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ...actions.engine import ActionEngine
from ...actions.results import RunResult
from ...config.config_manager import ConfigManager
from ..widgets.action_list import ActionList


class FlowView(QWidget):
    """Flow runner using actions tagged as 'flow'."""

    def __init__(
        self,
        config_manager: ConfigManager,
        action_engine: ActionEngine,
        log_callback,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.action_engine = action_engine
        self.log_callback = log_callback
        self.list_widget = ActionList()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Flows (actions tagged 'flow')"))
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.list_widget.run_requested.connect(self._run)
        self.list_widget.preview_requested.connect(self._preview)

        self.refresh()

    def refresh(self) -> None:
        flows = [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "favorite": a.favorite,
                "tags": a.tags,
                "hotkey": a.hotkey,
            }
            for a in self.action_engine.list_actions()
            if "flow" in a.tags
        ]
        self.list_widget.set_actions(flows)

    def filter_items(self, text: str) -> None:
        text_lower = text.lower()
        flows = [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "favorite": a.favorite,
                "tags": a.tags,
                "hotkey": a.hotkey,
            }
            for a in self.action_engine.list_actions()
            if "flow" in a.tags
            and (
                text_lower in a.name.lower()
                or text_lower in a.description.lower()
                or any(text_lower in t.lower() for t in a.tags)
            )
        ]
        self.list_widget.set_actions(flows)

    def _run(self, action_id: str) -> None:
        self.parent().run_action(action_id)  # type: ignore[attr-defined]

    def _preview(self, action_id: str) -> None:
        preview = self.action_engine.preview(action_id)
        result = RunResult(status="success")
        result.add_log("INFO", f"Preview for {preview.name}")
        for line in preview.lines:
            result.add_log("DEBUG", line)
        self.log_callback(result)
