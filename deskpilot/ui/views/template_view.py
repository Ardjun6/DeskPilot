from __future__ import annotations

from __future__ import annotations

from typing import Dict, Optional

from jinja2 import Template
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...actions.engine import ActionEngine
from ...actions.results import RunResult
from ...config.config_manager import ConfigManager
from ...config.models import TemplateDef
from ...utils.clipboard import copy_text


class TemplateView(QWidget):
    """Template form renderer with live preview and output options."""

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
        self.current_template: Optional[TemplateDef] = None

        self.template_picker = QComboBox()
        self.template_picker.currentIndexChanged.connect(self._on_template_changed)

        self.form_area = QWidget()
        self.form_layout = QFormLayout(self.form_area)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)

        self.btn_render = QPushButton("Render + Copy")
        self.btn_preview = QPushButton("Preview")
        self.btn_render.clicked.connect(self._render_and_copy)
        self.btn_preview.clicked.connect(self._do_preview)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.form_area)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Templates"))
        layout.addWidget(self.template_picker)
        layout.addWidget(scroll, 1)
        layout.addWidget(QLabel("Preview"))
        layout.addWidget(self.preview, 1)
        layout.addWidget(self.btn_render)
        layout.addWidget(self.btn_preview)
        self.setLayout(layout)

        self._load_templates()

    def _load_templates(self) -> None:
        self.template_picker.clear()
        for t in self.config_manager.templates.templates:
            self.template_picker.addItem(t.name, t)
        if self.config_manager.templates.templates:
            self._on_template_changed(0)

    def _on_template_changed(self, idx: int) -> None:
        template = self.template_picker.currentData()
        if not template:
            return
        self.current_template = template
        # rebuild form
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for field in template.fields:
            if field.type == "choice":
                widget = QComboBox()
                widget.addItems(field.choices)
                if field.default:
                    widget.setCurrentText(field.default)
            elif field.type == "multiline":
                widget = QTextEdit()
                if field.default:
                    widget.setPlainText(field.default)
            else:
                widget = QLineEdit()
                if field.default:
                    widget.setText(field.default)
            widget.setProperty("required", field.required)
            widget.setProperty("field_key", field.key)
            self.form_layout.addRow(field.label, widget)
        self.preview.clear()

    def _collect_inputs(self) -> Dict[str, str]:
        data: Dict[str, str] = {}
        for i in range(self.form_layout.count()):
            item = self.form_layout.itemAt(i)
            widget = item.widget()
            if widget is None:
                continue
            key = widget.property("field_key")
            if isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            else:
                value = ""
            data[str(key)] = value
        return data

    def _render_template(self, data: Dict[str, str]) -> str:
        if not self.current_template:
            return ""
        tpl = Template(self.current_template.jinja)
        return tpl.render(**data)

    def _render_and_copy(self) -> None:
        inputs = self._collect_inputs()
        try:
            rendered = self._render_template(inputs)
            copy_text(rendered)
            result = RunResult(status="success", outputs={"rendered_text": rendered})
            result.add_log("INFO", f"Rendered template {self.current_template.name if self.current_template else ''}")
            self.log_callback(result)
            QMessageBox.information(self, "Copied", "Template rendered and copied to clipboard.")
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, "Render failed", str(e))

    def _do_preview(self) -> None:
        inputs = self._collect_inputs()
        try:
            rendered = self._render_template(inputs)
            self.preview.setPlainText(rendered)
            result = RunResult(status="success", outputs={"rendered_text": rendered})
            result.add_log("INFO", f"Previewed template {self.current_template.name if self.current_template else ''}")
            self.log_callback(result)
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, "Render failed", str(e))

    def filter_items(self, text: str) -> None:
        # filter templates by name/description by resetting dropdown
        current = text.lower()
        self.template_picker.clear()
        for t in self.config_manager.templates.templates:
            if current in t.name.lower() or current in t.category.lower():
                self.template_picker.addItem(t.name, t)
