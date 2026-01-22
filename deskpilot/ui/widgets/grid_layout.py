from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class GridCell(QFrame):
    def __init__(self, title: Optional[str] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "grid-cell")
        self.setFrameShape(QFrame.NoFrame)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        if title:
            label = QLabel(title)
            label.setObjectName("SectionTitle")
            self.layout.addWidget(label)


class GridCanvas(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(16)
        for row in range(3):
            self.grid.setRowStretch(row, 1)
        for col in range(3):
            self.grid.setColumnStretch(col, 1)

    def add_cell(
        self,
        row: int,
        col: int,
        *,
        row_span: int = 1,
        col_span: int = 1,
        title: Optional[str] = None,
    ) -> GridCell:
        cell = GridCell(title=title)
        self.grid.addWidget(cell, row, col, row_span, col_span)
        return cell
