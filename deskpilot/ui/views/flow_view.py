from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QMessageBox, QVBoxLayout, QWidget

from ...actions.engine import ActionEngine
from ...config.config_manager import ConfigManager
from ..json_editor import JsonEditorDialog
from ..widgets.action_list import ActionList
from ..widgets.grid_layout import GridCanvas
from ..widgets.preview_dialog import PreviewDialog
from ..theme_manager import ThemeManager


class FlowView(QWidget):
    """Flow runner using actions tagged as 'flow'."""

    def __init__(
        self,
        config_manager: ConfigManager,
        action_engine: ActionEngine,
        log_callback,
        theme_manager: ThemeManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.action_engine = action_engine
        self.log_callback = log_callback
        self.theme_manager = theme_manager
        self.list_widget = ActionList()

        grid = GridCanvas()
        list_cell = grid.add_cell(0, 0, row_span=3, col_span=2, title="Flows")
        intro = QLabel("Flows are actions tagged 'flow' and shown as multi-step runs.")
        intro.setObjectName("ActionDesc")
        list_cell.layout.addWidget(intro)
        list_cell.layout.addWidget(self.list_widget)

        detail_cell = grid.add_cell(0, 2, row_span=3, col_span=1, title="Flow guidance")
        tip_preview = QLabel("Use Preview to see the step-by-step flowchart before running.")
        tip_preview.setObjectName("ActionDesc")
        tip_explain = QLabel("What it does provides a detailed sequence with arrows.")
        tip_explain.setObjectName("ActionDesc")
        detail_cell.layout.addWidget(tip_preview)
        detail_cell.layout.addWidget(tip_explain)
        detail_cell.layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(grid)
        self.setLayout(layout)

        self.list_widget.run_requested.connect(self._run)
        self.list_widget.preview_requested.connect(self._preview)
        self.list_widget.explain_requested.connect(self._explain)
        self.list_widget.edit_requested.connect(self._open_editor)
        self.list_widget.delete_requested.connect(self._delete_action)

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
        main = self.window()
        if hasattr(main, "run_action"):
            main.run_action(action_id)  # type: ignore[attr-defined]

    def _preview(self, action_id: str) -> None:
        preview = self.action_engine.preview(action_id)
        dialog = PreviewDialog(
            title=f"Preview: {preview.name}",
            summary=f"Flow preview for {preview.name}.",
            steps=preview.lines,
            theme_manager=self.theme_manager,
            parent=self,
        )
        dialog.exec()

    def _explain(self, action_id: str) -> None:
        action = self.action_engine.get_action(action_id)
        if action is None:
            return
        preview = self.action_engine.preview(action_id)
        dialog = PreviewDialog(
            title=f"What it does: {action.name}",
            summary=action.description or "No description provided.",
            steps=preview.lines,
            theme_manager=self.theme_manager,
            parent=self,
        )
        dialog.exec()

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
