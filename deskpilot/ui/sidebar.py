"""Sidebar navigation with horizontal/vertical layouts."""
from __future__ import annotations

from typing import Optional, List, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QButtonGroup,
    QSizePolicy,
)


class NavButton(QPushButton):
    """Navigation button with icon and label."""
    
    def __init__(self, icon: str, label: str, tooltip: str = "", parent=None) -> None:
        super().__init__(parent)
        self.icon_text = icon
        self.label_text = label
        self.setCheckable(True)
        self.setToolTip(tooltip or label)
        self._is_horizontal = False
        self._update_display()
    
    def _update_display(self) -> None:
        if self._is_horizontal:
            self.setText(f"{self.icon_text} {self.label_text}")
        else:
            self.setText(f"{self.icon_text}\n{self.label_text}")
    
    def set_horizontal(self, horizontal: bool) -> None:
        self._is_horizontal = horizontal
        self._update_display()


class Sidebar(QWidget):
    """Navigation sidebar that supports both vertical and horizontal layouts."""

    section_changed = Signal(int)

    NAV_ITEMS: List[Tuple[str, str, str]] = [
        ("Actions", "⚡", "Actions & Launchers"),
        ("Templates", "📝", "Text templates"),
        ("Workflow", "🔧", "Visual workflow builder"),
        ("Recorder", "🎬", "Record actions"),
        ("Clipboard", "📋", "Clipboard history"),
        ("Edit JSON", "📄", "Edit launcher JSON"),
        ("Settings", "⚙️", "Preferences"),
    ]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._orientation = "left"
        self._buttons: List[NavButton] = []
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(4)
        
        self._build_buttons()
        self._button_group.idClicked.connect(self._on_button_clicked)
        
        if self._buttons:
            self._buttons[0].setChecked(True)

    def _build_buttons(self) -> None:
        for i, (label, icon, tooltip) in enumerate(self.NAV_ITEMS):
            btn = NavButton(icon, label, tooltip)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self._buttons.append(btn)
            self._button_group.addButton(btn, i)
            self._layout.addWidget(btn)
        
        self._layout.addStretch()

    def _on_button_clicked(self, button_id: int) -> None:
        self.section_changed.emit(button_id)

    def set_orientation(self, position: str) -> None:
        self._orientation = position
        is_horizontal = position in ("top", "bottom")
        
        if is_horizontal:
            new_layout = QHBoxLayout()
            new_layout.setContentsMargins(8, 4, 8, 4)
            new_layout.setSpacing(8)
        else:
            new_layout = QVBoxLayout()
            new_layout.setContentsMargins(8, 8, 8, 8)
            new_layout.setSpacing(4)
        
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        for btn in self._buttons:
            btn.set_horizontal(is_horizontal)
            btn.setParent(self)
            new_layout.addWidget(btn)
        
        new_layout.addStretch()
        
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        
        self.setLayout(new_layout)
        self._layout = new_layout
        
        if is_horizontal:
            self.setMaximumHeight(60)
            self.setMaximumWidth(16777215)
            for btn in self._buttons:
                btn.setMinimumWidth(100)
                btn.setMinimumHeight(40)
        else:
            self.setMaximumHeight(16777215)
            self.setMaximumWidth(140)
            for btn in self._buttons:
                btn.setMinimumWidth(0)
                btn.setMinimumHeight(50)

    def select_index(self, index: int) -> None:
        if 0 <= index < len(self._buttons):
            self._buttons[index].setChecked(True)

    def current_index(self) -> int:
        return self._button_group.checkedId()
