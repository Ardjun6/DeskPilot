from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget, QSizePolicy


class GridCell(QFrame):
    """Styled card cell for grid layouts with title and content area."""

    def __init__(self, title: Optional[str] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "grid-cell")
        self.setFrameShape(QFrame.NoFrame)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(14)
        
        if title:
            label = QLabel(title)
            label.setObjectName("SectionTitle")
            self.layout.addWidget(label)

    def set_title(self, title: str) -> None:
        """Update the cell title."""
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.objectName() == "SectionTitle":
                widget.setText(title)
                return


class GridCanvas(QWidget):
    """Responsive grid layout container for arranging cells."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setSpacing(16)
        
        # Set up stretch factors for responsiveness
        for row in range(3):
            self.grid.setRowStretch(row, 1)
        for col in range(3):
            self.grid.setColumnStretch(col, 1)
        
        # Minimum column widths for usability
        self.grid.setColumnMinimumWidth(0, 200)
        self.grid.setColumnMinimumWidth(1, 200)
        self.grid.setColumnMinimumWidth(2, 180)

    def add_cell(
        self,
        row: int,
        col: int,
        *,
        row_span: int = 1,
        col_span: int = 1,
        title: Optional[str] = None,
    ) -> GridCell:
        """Add a cell to the grid at the specified position."""
        cell = GridCell(title=title)
        cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid.addWidget(cell, row, col, row_span, col_span)
        return cell

    def set_column_stretch(self, col: int, stretch: int) -> None:
        """Set the stretch factor for a column."""
        self.grid.setColumnStretch(col, stretch)
