from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QLabel, QPushButton, QVBoxLayout, QWidget

from ...actions.engine import ActionEngine
from ...actions.results import RunResult
from ...actions.steps import LaunchProfileStep, StepContext, CancelToken
from ...config.config_manager import ConfigManager
from ..widgets.grid_layout import GridCanvas


class LaunchView(QWidget):
    """Profiles launcher backed by config/profiles.json."""

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
        self.run_button.setProperty("primary", True)
        self.run_button.clicked.connect(self._run_selected)
        self.pick_button = QPushButton("Pick app (copy path)")
        self.pick_button.clicked.connect(self._pick_app)

        grid = GridCanvas()
        list_cell = grid.add_cell(0, 0, row_span=3, col_span=2, title="Launch Profiles")
        intro = QLabel("Launchers run a bundle of apps or URLs in sequence.")
        intro.setObjectName("ActionDesc")
        list_cell.layout.addWidget(intro)
        list_cell.layout.addWidget(self.list_widget, 1)
        list_cell.layout.addWidget(self.run_button)
        list_cell.layout.addWidget(self.pick_button)

        detail_cell = grid.add_cell(0, 2, row_span=3, col_span=1, title="Launcher tips")
        tip_profiles = QLabel("Profiles launch multiple targets together.")
        tip_profiles.setObjectName("ActionDesc")
        tip_pick = QLabel("Use \"Pick app\" to copy paths for new profiles.")
        tip_pick.setObjectName("ActionDesc")
        detail_cell.layout.addWidget(tip_profiles)
        detail_cell.layout.addWidget(tip_pick)
        detail_cell.layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(grid)
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
