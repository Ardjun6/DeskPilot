from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
)

from ..theme_manager import ThemeManager
from .flowchart_renderer import FlowchartWidget
from .grid_layout import GridCanvas


class PreviewDialog(QDialog):
    """Preview dialog showing action/macro steps with flowchart visualization."""

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
        self.setModal(True)

        self._build_ui(title, summary, steps)
        self.resize(900, 580)

    def _build_ui(self, title: str, summary: str, steps: List[str]) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title_label = QLabel(f"👁 {title}")
        title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        header.addWidget(title_label)
        header.addStretch()
        
        step_count = QLabel(f"{len(steps)} steps")
        step_count.setObjectName("ActionDesc")
        step_count.setStyleSheet("font-size: 12px;")
        header.addWidget(step_count)
        layout.addLayout(header)

        # Grid content
        grid = GridCanvas()
        
        # Summary cell
        summary_cell = grid.add_cell(0, 0, row_span=1, col_span=3, title="📋 Overview")
        self.summary_label = QLabel(summary)
        self.summary_label.setWordWrap(True)
        self.summary_label.setObjectName("ActionDesc")
        summary_cell.layout.addWidget(self.summary_label)

        # Steps list cell
        steps_cell = grid.add_cell(1, 0, row_span=2, col_span=2, title="📝 Step Sequence")
        self.step_list = QListWidget()
        self.step_list.setObjectName("StepList")
        self.step_list.setAlternatingRowColors(True)
        
        for idx, step in enumerate(steps, start=1):
            item = QListWidgetItem(f"  {idx}.  {step}")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.step_list.addItem(item)
        
        steps_cell.layout.addWidget(self.step_list)

        # Flowchart cell
        flow_cell = grid.add_cell(1, 2, row_span=2, col_span=1, title="📊 Flowchart")
        self.flowchart = FlowchartWidget(self.theme_manager)
        self.flowchart.set_steps(steps)
        flow_cell.layout.addWidget(self.flowchart)

        layout.addWidget(grid, 1)

        # Footer buttons
        footer = QHBoxLayout()
        footer.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.reject)
        footer.addWidget(close_btn)
        
        layout.addLayout(footer)
