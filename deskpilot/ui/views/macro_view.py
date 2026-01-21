from __future__ import annotations

import re
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...actions.macro_engine import MacroEngine
from ...actions.results import RunResult
from ...config.config_manager import ConfigManager
from ...config.models import MacroDef
from ..executor import MacroExecutionWorker
from ..json_editor import JsonEditorDialog
from ..widgets.action_list import ActionList


class MacroView(QWidget):
    """Macro list with run/preview and JSON editor access."""

    def __init__(
        self,
        config_manager: ConfigManager,
        macro_engine: MacroEngine,
        log_callback,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.macro_engine = macro_engine
        self.log_callback = log_callback
        self.current_worker: Optional[MacroExecutionWorker] = None

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search macros...")
        self.list_widget = ActionList()
        self.edit_button = QPushButton("Edit macros.json")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)

        header = QHBoxLayout()
        header.addWidget(self.search, 1)
        header.addWidget(self.edit_button)
        header.addWidget(self.stop_button)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.search.textChanged.connect(self.filter_items)
        self.list_widget.run_requested.connect(self._run_macro)
        self.list_widget.preview_requested.connect(self._preview_macro)
        self.edit_button.clicked.connect(self._open_editor)
        self.stop_button.clicked.connect(self._stop_worker)

        self.refresh()

    def refresh(self) -> None:
        macros = self.macro_engine.list_macros()
        actions = [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "favorite": False,
                "tags": [m.category, m.safety],
                "hotkey": m.hotkey,
            }
            for m in macros
        ]
        self.list_widget.set_actions(actions)

    def filter_items(self, text: str) -> None:
        text_lower = text.lower()
        macros = [
            m
            for m in self.macro_engine.list_macros()
            if text_lower in m.name.lower()
            or text_lower in m.description.lower()
            or text_lower in m.category.lower()
        ]
        actions = [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "favorite": False,
                "tags": [m.category, m.safety],
                "hotkey": m.hotkey,
            }
            for m in macros
        ]
        self.list_widget.set_actions(actions)

    def _run_macro(self, macro_id: str) -> None:
        macro = self.macro_engine.get_macro(macro_id)
        if macro is None:
            return
        inputs = self._prompt_placeholders(macro)
        worker = MacroExecutionWorker(self.macro_engine, macro_id, inputs=inputs)
        self.current_worker = worker
        self.stop_button.setEnabled(True)
        worker.finished_with_result.connect(self._on_finished)
        worker.start()

    def _preview_macro(self, macro_id: str) -> None:
        lines = self.macro_engine.preview(macro_id)
        result = RunResult(status="success")
        result.add_log("INFO", f"Preview for macro {macro_id}")
        for line in lines:
            result.add_log("DEBUG", line)
        self.log_callback(result)

    def _on_finished(self, result: RunResult) -> None:
        self.stop_button.setEnabled(False)
        self.current_worker = None
        self.log_callback(result)

    def _stop_worker(self) -> None:
        if self.current_worker:
            self.current_worker.request_cancel()

    def _prompt_placeholders(self, macro: MacroDef) -> Dict[str, str]:
        inputs: Dict[str, str] = {}
        pattern = re.compile(r"{([^}]+)}")
        placeholders: set[str] = set()
        for step in macro.steps:
            for value in step.params.values():
                if isinstance(value, str):
                    placeholders.update(pattern.findall(value))
        for ph in sorted(placeholders):
            text, ok = self._prompt_text(f"Value for {ph}", f"Enter value for {{{ph}}}:")
            if not ok:
                return {}
            inputs[ph] = text
        return inputs

    def _prompt_text(self, title: str, label: str):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        edit = QLineEdit()
        lbl = QLabel(label)
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        hl = QHBoxLayout()
        hl.addWidget(btn_ok)
        hl.addWidget(btn_cancel)
        layout = QVBoxLayout(dlg)
        layout.addWidget(lbl)
        layout.addWidget(edit)
        layout.addLayout(hl)

        chosen = {"ok": False}

        def accept():
            chosen["ok"] = True
            dlg.accept()

        btn_ok.clicked.connect(accept)
        btn_cancel.clicked.connect(dlg.reject)
        dlg.exec()
        return edit.text(), chosen["ok"]

    def _open_editor(self) -> None:
        dialog = JsonEditorDialog(
            path=self.config_manager.macros_path,
            loader=lambda text: self.config_manager.macros.model_validate_json(text),
            formatter=lambda data: self.config_manager.macros.model_validate(data).model_dump(),
            parent=self,
        )
        dialog.exec()
        # reload file after editing
        self.config_manager.macros = dialog.reload_model(self.config_manager.macros_path, self.config_manager.macros)
        self.refresh()
