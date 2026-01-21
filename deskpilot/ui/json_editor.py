from __future__ import annotations

import json
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)


class JsonEditorDialog(QDialog):
    """Simple JSON editor with validation and save-on-close rules."""

    def __init__(
        self,
        path,
        loader: Callable[[str], object],
        formatter: Optional[Callable[[object], object]] = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Edit {path.name}")
        self.path = path
        self.loader = loader
        self.formatter = formatter or (lambda data: data)
        self.original_text = path.read_text(encoding="utf-8") if path.exists() else "{}"
        self.last_valid_text = self.original_text
        self._dirty = False

        self.editor = QPlainTextEdit(self.original_text)
        self.status = QLabel("")
        self.status.setObjectName("ActionDesc")

        btn_save_close = QPushButton("Save && Close")
        btn_keep = QPushButton("Keep Editing")
        btn_reload = QPushButton("Reload from disk")
        btn_format = QPushButton("Format JSON")
        btn_validate = QPushButton("Validate")

        btn_save_close.clicked.connect(self._save_and_close)
        btn_keep.clicked.connect(lambda: None)
        btn_reload.clicked.connect(self._reload)
        btn_format.clicked.connect(self._format_json)
        btn_validate.clicked.connect(self._validate)

        buttons = QHBoxLayout()
        buttons.addWidget(btn_save_close)
        buttons.addWidget(btn_keep)
        buttons.addWidget(btn_reload)
        buttons.addWidget(btn_format)
        buttons.addWidget(btn_validate)

        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)
        layout.addLayout(buttons)
        layout.addWidget(self.status)

        self.editor.textChanged.connect(self._mark_dirty)

    def _mark_dirty(self) -> None:
        self._dirty = self.editor.toPlainText() != self.original_text

    def _reload(self) -> None:
        self.editor.setPlainText(self.path.read_text(encoding="utf-8"))
        self._mark_dirty()
        self.status.setText("Reloaded from disk.")

    def _format_json(self) -> None:
        try:
            obj = json.loads(self.editor.toPlainText())
            formatted = json.dumps(obj, indent=2)
            self.editor.setPlainText(formatted)
            self.status.setText("Formatted.")
            self._mark_dirty()
        except Exception as e:  # noqa: BLE001
            self.status.setText(f"Format failed: {e}")

    def _validate(self) -> bool:
        try:
            text = self.editor.toPlainText()
            self.loader(text)  # pydantic parsing if provided
            self.status.setText("Valid JSON.")
            self.last_valid_text = text
            return True
        except Exception as e:  # noqa: BLE001
            self.status.setText(f"Validation error: {e}")
            return False

    def _save(self) -> bool:
        try:
            text = self.editor.toPlainText()
            obj = json.loads(text)
            obj = self.formatter(obj)
            formatted = json.dumps(obj, indent=2)
            self.path.write_text(formatted, encoding="utf-8")
            self.original_text = formatted
            self.editor.setPlainText(formatted)
            self._dirty = False
            self.status.setText("Saved.")
            return True
        except Exception as e:  # noqa: BLE001
            self.status.setText(f"Save failed: {e}")
            return False

    def _save_and_close(self) -> None:
        if self._save():
            self.accept()

    def closeEvent(self, event) -> None:  # noqa: N802
        if not self._dirty:
            event.accept()
            return
        is_valid = self._validate()
        if not is_valid:
            QMessageBox.warning(self, "Invalid JSON", "Fix validation errors before closing.")
            event.ignore()
            return
        # Dirty + valid => require save
        QMessageBox.information(self, "Save required", "You made changes. Save before closing.")
        event.ignore()

    def reload_model(self, path, fallback):
        try:
            return self.loader(path.read_text(encoding="utf-8"))
        except Exception:
            return fallback
