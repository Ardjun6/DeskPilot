from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget, QMessageBox

from ...actions.engine import ActionEngine
from ...config.config_manager import ConfigManager
from ..json_editor import JsonEditorDialog
from ..widgets.action_list import ActionList
from ..widgets.grid_layout import GridCanvas


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
        self.scroll = scroll

        self.empty = QLabel("No actions found. Add entries to actions.json.")
        self.empty.setObjectName("ActionDesc")

        grid = GridCanvas()
        list_cell = grid.add_cell(0, 0, row_span=3, col_span=2, title="Actions")
        list_cell.layout.addWidget(scroll)
        list_cell.layout.addWidget(self.empty)
        self.list_cell = list_cell

        detail_cell = grid.add_cell(0, 2, row_span=3, col_span=1, title="Action guidance")
        tip_preview = QLabel("Preview shows steps and a flowchart before running.")
        tip_preview.setObjectName("ActionDesc")
        tip_explain = QLabel("What it does provides the detailed sequence for review.")
        tip_explain.setObjectName("ActionDesc")
        detail_cell.layout.addWidget(tip_preview)
        detail_cell.layout.addWidget(tip_explain)
        detail_cell.layout.addStretch()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(grid)
        self.setLayout(layout)

        self.list_widget.run_requested.connect(self._emit_run)
        self.list_widget.preview_requested.connect(self._emit_preview)
        self.list_widget.explain_requested.connect(self._emit_explain)
        self.list_widget.edit_requested.connect(self._open_editor)
        self.list_widget.delete_requested.connect(self._delete_action)

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
            self.scroll.hide()
            self.empty.show()
        else:
            self.empty.hide()
            self.scroll.show()
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
        main = self.window()
        if hasattr(main, "run_action"):
            main.run_action(action_id)  # type: ignore[attr-defined]

    def _emit_preview(self, action_id: str) -> None:
        main = self.window()
        if hasattr(main, "preview_action"):
            main.preview_action(action_id)  # type: ignore[attr-defined]

    def _emit_explain(self, action_id: str) -> None:
        main = self.window()
        if hasattr(main, "explain_action"):
            main.explain_action(action_id)  # type: ignore[attr-defined]

    def _open_editor(self, action_id: str) -> None:
        dialog = JsonEditorDialog(
            path=self.config_manager.actions_path,
            loader=lambda text: self.config_manager.actions.model_validate_json(text),
            formatter=lambda data: self.config_manager.actions.model_validate(data).model_dump(),
            parent=self,
        )
        dialog.exec()
        self.config_manager.actions = dialog.reload_model(self.config_manager.actions_path, self.config_manager.actions)
        self.refresh()

    def _delete_action(self, action_id: str) -> None:
        action = self.action_engine.get_action(action_id)
        if action is None:
            return
        confirm = QMessageBox.question(
            self,
            "Delete action",
            f"Delete '{action.name}'? This will remove it from actions.json.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        self.config_manager.actions.actions = [
            existing for existing in self.config_manager.actions.actions if existing.id != action_id
        ]
        self.config_manager.save_all()
        self.refresh()
