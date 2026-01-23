from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..widgets.grid_layout import GridCanvas


class TestView(QWidget):
    """Lightweight UI sandbox for quick manual checks."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        grid = GridCanvas()

        control_cell = grid.add_cell(0, 0, row_span=3, col_span=2, title="Test controls")
        intro = QLabel("Use this panel to sanity-check widgets, layout, and theme styling.")
        intro.setObjectName("ActionDesc")
        control_cell.layout.addWidget(intro)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Type here to check input styling")
        control_cell.layout.addWidget(self.name_edit)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Quick", "Full", "Custom"])
        control_cell.layout.addWidget(self.mode_combo)

        self.flag_check = QCheckBox("Enable extra option")
        control_cell.layout.addWidget(self.flag_check)

        button_row = QHBoxLayout()
        self.run_button = QPushButton("Run test")
        self.preview_button = QPushButton("Preview")
        self.reset_button = QPushButton("Reset")
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.preview_button)
        button_row.addWidget(self.reset_button)
        control_cell.layout.addLayout(button_row)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Test output will appear here.")
        control_cell.layout.addWidget(self.output)

        checklist_cell = grid.add_cell(0, 2, row_span=3, col_span=1, title="Checklist")
        checklist = [
            "Buttons highlight on hover and click.",
            "Inputs show focus ring and caret.",
            "Theme colors apply to labels and panels.",
            "Spacing feels even across the grid.",
            "Shortcuts work: Ctrl+Shift+T and Ctrl+Shift+P.",
        ]
        for item in checklist:
            label = QLabel(f"- {item}")
            label.setObjectName("ActionDesc")
            checklist_cell.layout.addWidget(label)
        checklist_cell.layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(grid)
        self.setLayout(layout)

        self.run_button.clicked.connect(self._run_test)
        self.preview_button.clicked.connect(self._preview_test)
        self.reset_button.clicked.connect(self._reset_test)
        self._bind_shortcuts()

    def _bind_shortcuts(self) -> None:
        run_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        run_shortcut.activated.connect(self._run_test)
        preview_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        preview_shortcut.activated.connect(self._preview_test)

    def _run_test(self) -> None:
        name = self.name_edit.text().strip() or "unnamed"
        mode = self.mode_combo.currentText()
        flag = "on" if self.flag_check.isChecked() else "off"
        self.output.appendPlainText(f"Test run: name={name}, mode={mode}, option={flag}")

    def _preview_test(self) -> None:
        self.output.appendPlainText("Preview opened.")
        QMessageBox.information(self, "Preview", "This is a sample preview dialog.")

    def _reset_test(self) -> None:
        self.name_edit.clear()
        self.mode_combo.setCurrentIndex(0)
        self.flag_check.setChecked(False)
        self.output.clear()

    def filter_items(self, text: str) -> None:
        _ = text
