from __future__ import annotations

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from ...actions.engine import ActionEngine
from ...actions.results import RunResult
from ...actions.steps import LaunchProfileStep, StepContext, CancelToken
from ...config.config_manager import ConfigManager


class LaunchView(QWidget):
    """Profiles launcher backed by config/profiles.yaml."""

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

        self.list_widget = QListWidget()
        self.run_button = QPushButton("Run profile")
        self.run_button.clicked.connect(self._run_selected)
        self.pick_button = QPushButton("Pick app (copy path)")
        self.pick_button.clicked.connect(self._pick_app)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.run_button)
        layout.addWidget(self.pick_button)
        self.setLayout(layout)

        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for name, targets in self.config_manager.profiles.profiles.items():
            item = QListWidgetItem(f"{name} ({len(targets)} targets)")
            item.setData(0, name)
            self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def filter_items(self, text: str) -> None:
        text_lower = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            visible = text_lower in item.text().lower()
            item.setHidden(not visible)

    def _run_selected(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            return
        profile = item.data(0)
        self._run_profile_name(profile)

    def _run_profile_name(self, profile: str) -> None:
        step = LaunchProfileStep(profile=profile)
        ctx = StepContext(config=self.config_manager, inputs={}, cancel=CancelToken(), dry_run=False)
        result = RunResult(status="success")
        step.run(ctx, result)
        self.log_callback(result)

    def _pick_app(self) -> None:
        from ..widgets.app_picker import AppPickerDialog
        from ...utils.clipboard import copy_text

        dlg = AppPickerDialog(self)
        if dlg.exec():
            path = dlg.selected_path()
            if path:
                copy_text(path)
