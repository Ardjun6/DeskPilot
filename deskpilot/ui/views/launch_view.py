from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from PySide6.QtCore import QThread, Signal, QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

import pyautogui

from ...actions.engine import ActionEngine
from ...actions.results import RunResult
from ...actions.steps import CancelToken, StepContext, step_from_def
from ...config.config_manager import ConfigManager
from ..theme_manager import ThemeManager
from ..widgets.flowchart_renderer import FlowchartWidget
from ..widgets.grid_layout import GridCanvas
from ..widgets.preview_dialog import PreviewDialog


@dataclass
class LauncherStep:
    type: str
    params: dict[str, Any]


class LauncherExecutionWorker(QThread):
    finished_with_result = Signal(RunResult)

    def __init__(
        self,
        *,
        config_manager: ConfigManager,
        steps: list[LauncherStep],
        schedule_time: Optional[str],
        schedule_delay: Optional[int],
    ) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.steps = steps
        self.schedule_time = schedule_time
        self.schedule_delay = schedule_delay
        self.cancel_token = CancelToken()

    def request_cancel(self) -> None:
        self.cancel_token.cancelled = True

    def run(self) -> None:
        ctx = StepContext(config=self.config_manager, inputs={}, dry_run=False, cancel=self.cancel_token)
        result = RunResult(status="success")
        ordered_steps = self._build_steps()
        result.add_log("INFO", "Running launcher sequence")
        for step in ordered_steps:
            if ctx.cancel.cancelled:
                result.status = "cancelled"
                result.add_log("WARNING", "Cancelled", getattr(step, "type", None))
                break
            try:
                result.add_log("DEBUG", step.preview(ctx), getattr(step, "type", None))
                step.run(ctx, result)
                if result.status == "failed":
                    break
            except Exception as exc:  # noqa: BLE001
                result.add_error(f"Step failed: {exc}", getattr(step, "type", None), type(exc).__name__)
                break
        self.finished_with_result.emit(result)

    def _build_steps(self):
        steps = []
        if self.schedule_time:
            steps.append(step_from_def("wait_until", {"time": self.schedule_time}))
        if self.schedule_delay:
            steps.append(step_from_def("delay", {"seconds": self.schedule_delay}))
        for step in self.steps:
            steps.append(step_from_def(step.type, dict(step.params)))
        return steps


class LaunchView(QWidget):
    """Launcher builder for custom app/click sequences."""

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
        self.steps: list[LauncherStep] = []
        self.current_worker: Optional[LauncherExecutionWorker] = None

        self.sequence_list = QListWidget()
        self.flowchart = FlowchartWidget(theme_manager)

        self.add_app_button = QPushButton("Add application")
        self.add_app_button.setProperty("primary", True)
        self.add_url_button = QPushButton("Add URL")
        self.add_click_button = QPushButton("Capture click")
        self.add_delay_button = QPushButton("Add delay")
        self.remove_button = QPushButton("Remove step")
        self.move_up_button = QPushButton("Move up")
        self.move_down_button = QPushButton("Move down")

        self.schedule_mode = QComboBox()
        self.schedule_mode.addItems(["Run now", "At time", "After delay"])
        self.schedule_time = QTimeEdit()
        self.schedule_time.setDisplayFormat("HH:mm")
        self.schedule_time.setTime(QTime.currentTime())
        self.schedule_delay = QSpinBox()
        self.schedule_delay.setRange(1, 24 * 60)
        self.schedule_delay.setSuffix(" min")
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("Hotkey (e.g., H or H+P)")

        self.run_button = QPushButton("Run launcher")
        self.run_button.setProperty("primary", True)
        self.preview_button = QPushButton("Preview")

        self._build_layout()
        self._connect_signals()
        self._refresh_sequence()

    def _build_layout(self) -> None:
        grid = GridCanvas()
        builder_cell = grid.add_cell(0, 0, row_span=3, col_span=2, title="Launcher Builder")
        intro = QLabel("Create a launch sequence by adding apps, URLs, clicks, and delays.")
        intro.setObjectName("ActionDesc")
        builder_cell.layout.addWidget(intro)

        builder_cell.layout.addWidget(self.sequence_list, 1)

        controls_row = QHBoxLayout()
        controls_row.addWidget(self.add_app_button)
        controls_row.addWidget(self.add_url_button)
        controls_row.addWidget(self.add_click_button)
        controls_row.addWidget(self.add_delay_button)
        builder_cell.layout.addLayout(controls_row)

        manage_row = QHBoxLayout()
        manage_row.addWidget(self.move_up_button)
        manage_row.addWidget(self.move_down_button)
        manage_row.addWidget(self.remove_button)
        builder_cell.layout.addLayout(manage_row)

        schedule_row = QHBoxLayout()
        schedule_row.addWidget(QLabel("Schedule"))
        schedule_row.addWidget(self.schedule_mode)
        schedule_row.addWidget(QLabel("Time"))
        schedule_row.addWidget(self.schedule_time)
        schedule_row.addWidget(QLabel("Delay"))
        schedule_row.addWidget(self.schedule_delay)
        schedule_row.addWidget(QLabel("Hotkey"))
        schedule_row.addWidget(self.hotkey_input)
        builder_cell.layout.addLayout(schedule_row)

        action_row = QHBoxLayout()
        action_row.addWidget(self.preview_button)
        action_row.addWidget(self.run_button)
        builder_cell.layout.addLayout(action_row)

        preview_cell = grid.add_cell(0, 2, row_span=3, col_span=1, title="Flow Preview")
        preview_tip = QLabel("Arrows show the order in which your launch steps will run.")
        preview_tip.setObjectName("ActionDesc")
        preview_cell.layout.addWidget(preview_tip)
        preview_cell.layout.addWidget(self.flowchart, 1)

        layout = QVBoxLayout()
        layout.addWidget(grid)
        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self.add_app_button.clicked.connect(self._add_app)
        self.add_url_button.clicked.connect(self._add_url)
        self.add_click_button.clicked.connect(self._capture_click)
        self.add_delay_button.clicked.connect(self._add_delay)
        self.remove_button.clicked.connect(self._remove_step)
        self.move_up_button.clicked.connect(lambda: self._move_step(-1))
        self.move_down_button.clicked.connect(lambda: self._move_step(1))
        self.preview_button.clicked.connect(self._preview_sequence)
        self.run_button.clicked.connect(self._run_sequence)
        self.schedule_mode.currentTextChanged.connect(self._toggle_schedule)
        self._toggle_schedule(self.schedule_mode.currentText())

    def refresh(self) -> None:
        self._refresh_sequence()

    def filter_items(self, text: str) -> None:
        _ = text

    def _toggle_schedule(self, mode: str) -> None:
        self.schedule_time.setEnabled(mode == "At time")
        self.schedule_delay.setEnabled(mode == "After delay")

    def _add_app(self) -> None:
        from ..widgets.app_picker import AppPickerDialog

        dlg = AppPickerDialog(self)
        if dlg.exec():
            path = dlg.selected_path()
            if path:
                self.steps.append(LauncherStep("open_app", {"path": path}))
                self._refresh_sequence()

    def _add_url(self) -> None:
        url, ok = self._prompt_text("Add URL", "Enter the URL to open:")
        if ok and url:
            self.steps.append(LauncherStep("open_url", {"url": url}))
            self._refresh_sequence()

    def _capture_click(self) -> None:
        QMessageBox.information(
            self,
            "Capture click",
            "Move your mouse to the target and press OK to capture its position.",
        )
        pos = pyautogui.position()
        self.steps.append(LauncherStep("click", {"x": int(pos.x), "y": int(pos.y)}))
        self._refresh_sequence()

    def _add_delay(self) -> None:
        minutes, ok = self._prompt_number("Add delay", "Delay (minutes):", 1, 1440)
        if ok:
            self.steps.append(LauncherStep("delay", {"seconds": int(minutes) * 60}))
            self._refresh_sequence()

    def _remove_step(self) -> None:
        row = self.sequence_list.currentRow()
        if 0 <= row < len(self.steps):
            self.steps.pop(row)
            self._refresh_sequence()

    def _move_step(self, offset: int) -> None:
        row = self.sequence_list.currentRow()
        new_row = row + offset
        if 0 <= row < len(self.steps) and 0 <= new_row < len(self.steps):
            self.steps[row], self.steps[new_row] = self.steps[new_row], self.steps[row]
            self._refresh_sequence()
            self.sequence_list.setCurrentRow(new_row)

    def _preview_sequence(self) -> None:
        steps = self._preview_lines()
        summary = "Launcher sequence preview."
        if self.hotkey_input.text().strip():
            summary += f" Hotkey: {self.hotkey_input.text().strip()}."
        if self.schedule_mode.currentText() == "At time":
            summary += f" Scheduled at {self.schedule_time.time().toString('HH:mm')}."
        elif self.schedule_mode.currentText() == "After delay":
            summary += f" Runs after {self.schedule_delay.value()} minute(s)."
        dialog = PreviewDialog(
            title="Launcher Preview",
            summary=summary,
            steps=steps,
            theme_manager=self.theme_manager,
            parent=self,
        )
        dialog.exec()

    def _run_sequence(self) -> None:
        if self.current_worker:
            return
        schedule_time, schedule_delay = self._schedule_values()
        worker = LauncherExecutionWorker(
            config_manager=self.config_manager,
            steps=self.steps,
            schedule_time=schedule_time,
            schedule_delay=schedule_delay,
        )
        self.current_worker = worker
        worker.finished_with_result.connect(self._on_finished)
        worker.start()

    def _on_finished(self, result: RunResult) -> None:
        self.current_worker = None
        self.log_callback(result)

    def _refresh_sequence(self) -> None:
        self.sequence_list.clear()
        for step in self.steps:
            item = QListWidgetItem(self._step_label(step))
            self.sequence_list.addItem(item)
        self.flowchart.set_steps(self._preview_lines())

    def _preview_lines(self) -> list[str]:
        ctx = StepContext(config=self.config_manager, inputs={}, dry_run=True)
        lines = []
        schedule_time, schedule_delay = self._schedule_values()
        if schedule_time:
            lines.append(step_from_def("wait_until", {"time": schedule_time}).preview(ctx))
        if schedule_delay:
            lines.append(step_from_def("delay", {"seconds": schedule_delay}).preview(ctx))
        for step in self.steps:
            lines.append(step_from_def(step.type, dict(step.params)).preview(ctx))
        return lines

    def _step_label(self, step: LauncherStep) -> str:
        ctx = StepContext(config=self.config_manager, inputs={}, dry_run=True)
        return step_from_def(step.type, dict(step.params)).preview(ctx)

    def _schedule_values(self) -> tuple[Optional[str], Optional[int]]:
        mode = self.schedule_mode.currentText()
        if mode == "At time":
            return self.schedule_time.time().toString("HH:mm"), None
        if mode == "After delay":
            return None, int(self.schedule_delay.value() * 60)
        return None, None

    def _prompt_text(self, title: str, label: str) -> tuple[str, bool]:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        edit = QLineEdit()
        lbl = QLabel(label)
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        row = QHBoxLayout()
        row.addWidget(btn_ok)
        row.addWidget(btn_cancel)
        layout = QVBoxLayout(dialog)
        layout.addWidget(lbl)
        layout.addWidget(edit)
        layout.addLayout(row)
        chosen = {"ok": False}

        def accept() -> None:
            chosen["ok"] = True
            dialog.accept()

        btn_ok.clicked.connect(accept)
        btn_cancel.clicked.connect(dialog.reject)
        dialog.exec()
        return edit.text().strip(), chosen["ok"]

    def _prompt_number(self, title: str, label: str, min_value: int, max_value: int) -> tuple[int, bool]:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        spin = QSpinBox()
        spin.setRange(min_value, max_value)
        lbl = QLabel(label)
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        row = QHBoxLayout()
        row.addWidget(btn_ok)
        row.addWidget(btn_cancel)
        layout = QVBoxLayout(dialog)
        layout.addWidget(lbl)
        layout.addWidget(spin)
        layout.addLayout(row)
        chosen = {"ok": False}

        def accept() -> None:
            chosen["ok"] = True
            dialog.accept()

        btn_ok.clicked.connect(accept)
        btn_cancel.clicked.connect(dialog.reject)
        dialog.exec()
        return int(spin.value()), chosen["ok"]
