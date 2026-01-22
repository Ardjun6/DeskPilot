from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from ...config.config_manager import ConfigManager
from ...config.models import MacroDef


class MacroEditorDialog(QDialog):
    def __init__(
        self,
        *,
        config_manager: ConfigManager,
        macro: MacroDef,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.macro = macro
        self.setWindowTitle(f"Edit macro schedule: {macro.name}")
        self.setObjectName("MacroEditorDialog")

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["None", "At time", "After delay"])

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())

        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 24 * 60)
        self.delay_spin.setSuffix(" min")

        self.app_title = QLineEdit()
        self.app_title.setPlaceholderText("Window title contains (e.g., Chrome, Excel)")

        form = QFormLayout()
        form.addRow(QLabel("Schedule"), self.mode_combo)
        form.addRow(QLabel("Time"), self.time_edit)
        form.addRow(QLabel("Delay"), self.delay_spin)
        form.addRow(QLabel("Focus app"), self.app_title)

        helper = QLabel(
            "Scheduled macros wait for the chosen time or delay, then focus the target app before running steps."
        )
        helper.setWordWrap(True)
        helper.setObjectName("ActionDesc")

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(helper)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._load_from_macro()
        self.mode_combo.currentTextChanged.connect(self._toggle_fields)
        self._toggle_fields(self.mode_combo.currentText())

    def _load_from_macro(self) -> None:
        if self.macro.schedule_time:
            self.mode_combo.setCurrentText("At time")
            try:
                hours, minutes = self.macro.schedule_time.split(":")
                self.time_edit.setTime(QTime(int(hours), int(minutes)))
            except ValueError:
                self.time_edit.setTime(QTime.currentTime())
        elif self.macro.schedule_delay:
            self.mode_combo.setCurrentText("After delay")
            minutes = max(1, int(self.macro.schedule_delay // 60))
            self.delay_spin.setValue(minutes)
        else:
            self.mode_combo.setCurrentText("None")
        self.app_title.setText(self.macro.app_title or "")

    def _toggle_fields(self, mode: str) -> None:
        self.time_edit.setEnabled(mode == "At time")
        self.delay_spin.setEnabled(mode == "After delay")

    def _save(self) -> None:
        mode = self.mode_combo.currentText()
        if mode == "At time":
            time_text = self.time_edit.time().toString("HH:mm")
            self.macro.schedule_time = time_text
            self.macro.schedule_delay = None
        elif mode == "After delay":
            delay_seconds = int(self.delay_spin.value() * 60)
            self.macro.schedule_delay = delay_seconds
            self.macro.schedule_time = None
        else:
            self.macro.schedule_time = None
            self.macro.schedule_delay = None

        app_title = self.app_title.text().strip()
        self.macro.app_title = app_title if app_title else None

        self.config_manager.save_all()
        self.accept()
