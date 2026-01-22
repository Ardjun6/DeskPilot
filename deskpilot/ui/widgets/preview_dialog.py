from __future__ import annotations

from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..theme_manager import ThemeManager
from .flowchart_renderer import FlowchartWidget
from .grid_layout import GridCanvas


class PreviewDialog(QDialog):
    def __init__(
        self,
        *,
        title: str,
        summary: str,
        steps: List[str],
        theme_manager: ThemeManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle(title)
        self.setObjectName("PreviewDialog")

        self.summary_label = QLabel(summary)
        self.summary_label.setWordWrap(True)
        self.summary_label.setObjectName("ActionDesc")

        self.step_list = QListWidget()
        self.step_list.setObjectName("StepList")
        for idx, step in enumerate(steps, start=1):
            item = QListWidgetItem(f"{idx}. {step}")
            self.step_list.addItem(item)

        self.flowchart = FlowchartWidget(theme_manager)
        self.flowchart.set_steps(steps)

        grid = GridCanvas()
        summary_cell = grid.add_cell(0, 0, row_span=1, col_span=3, title="Overview")
        summary_cell.layout.addWidget(self.summary_label)

        steps_cell = grid.add_cell(1, 0, row_span=2, col_span=2, title="Step Sequence")
        steps_cell.layout.addWidget(self.step_list)

        flow_cell = grid.add_cell(1, 2, row_span=2, col_span=1, title="Flowchart")
        flow_cell.layout.addWidget(self.flowchart)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(grid)
        layout.addWidget(buttons)
        self.resize(860, 560)
