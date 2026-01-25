"""
Visual Workflow Builder - Clean, modern design with all improvements.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from PySide6.QtCore import Qt, Signal, QTimer, QMimeData
from PySide6.QtGui import QPainter, QColor, QPen, QDrag, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QApplication,
    QCheckBox,
    QTimeEdit,
)

from ...config.config_manager import ConfigManager
from ..theme_manager import ThemeManager
from ..widgets.app_picker import AppPickerDialog
from ..widgets.coordinate_picker import CoordinatePicker


# ============================================================================
# STEP TYPE DEFINITIONS
# ============================================================================
STEP_TYPES = {
    "open_app": {"name": "Open Application", "icon": "🖥️", "desc": "Launch an application"},
    "open_url": {"name": "Open URL", "icon": "🌐", "desc": "Open a website"},
    "delay": {"name": "Wait / Delay", "icon": "⏱️", "desc": "Pause for seconds"},
    "click": {"name": "Mouse Click", "icon": "🖱️", "desc": "Click at position"},
    "type_text": {"name": "Type Text", "icon": "⌨️", "desc": "Type text at cursor"},
    "hotkey": {"name": "Press Hotkey", "icon": "🔤", "desc": "Press key combination"},
    "paste": {"name": "Paste Clipboard", "icon": "📋", "desc": "Paste from clipboard"},
    "paste_history": {"name": "Paste from History", "icon": "📑", "desc": "Paste specific history item"},
    "jiggle": {"name": "Mouse Jiggler", "icon": "🔄", "desc": "Keep PC awake"},
}


@dataclass
class WorkflowStep:
    """A single step in the workflow."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = "delay"
    params: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def display_name(self) -> str:
        return STEP_TYPES.get(self.type, {}).get("name", self.type)
    
    @property
    def icon(self) -> str:
        return STEP_TYPES.get(self.type, {}).get("icon", "❓")
    
    def clone(self) -> "WorkflowStep":
        return WorkflowStep(type=self.type, params=dict(self.params))


# ============================================================================
# STEP BLOCK WIDGET
# ============================================================================
class StepBlock(QFrame):
    """Visual block for a workflow step."""
    
    edit_requested = Signal(object)
    delete_requested = Signal(str)
    duplicate_requested = Signal(object)
    drag_started = Signal(object)
    selected = Signal(object)
    move_requested = Signal(object, int)  # step, direction (-1 up, +1 down)
    
    def __init__(self, step: WorkflowStep, index: int, colors: dict, parent=None) -> None:
        super().__init__(parent)
        self.step = step
        self.index = index
        self.colors = colors
        self._is_selected = False
        self.setFixedHeight(56)
        self.setCursor(Qt.OpenHandCursor)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setAcceptDrops(True)
        self._drag_start_pos = None
        self.drop_index = index  # For drop handling
        self.drop_handler = None  # Set by parent
        self._build_ui()
    
    def _build_ui(self) -> None:
        self._update_style()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)
        
        # Drag handle
        drag = QLabel("⋮⋮")
        drag.setStyleSheet(f"color: {self.colors['text_muted']}; font-size: 10px;")
        layout.addWidget(drag)
        
        # Step number
        num = QLabel(str(self.index + 1))
        num.setFixedSize(18, 18)
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet(f"""
            background: {self.colors['bg_alt']};
            color: {self.colors['text_muted']};
            border-radius: 9px;
            font-size: 9px;
            font-weight: 600;
        """)
        layout.addWidget(num)
        
        # Icon
        icon = QLabel(self.step.icon)
        icon.setStyleSheet("font-size: 14px;")
        layout.addWidget(icon)
        
        # Info
        info = QVBoxLayout()
        info.setSpacing(0)
        
        name = QLabel(self.step.display_name)
        name.setStyleSheet(f"font-weight: 500; font-size: 11px; color: {self.colors['text']};")
        info.addWidget(name)
        
        preview = QLabel(self._get_preview())
        preview.setStyleSheet(f"font-size: 9px; color: {self.colors['text_muted']};")
        info.addWidget(preview)
        
        layout.addLayout(info, 1)
        
        # Buttons
        btn_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: {self.colors['bg_alt']}; }}
        """
        
        # Move up button
        up_btn = QPushButton("▲")
        up_btn.setFixedSize(20, 20)
        up_btn.setToolTip("Move up")
        up_btn.setStyleSheet(btn_style)
        up_btn.clicked.connect(lambda: self.move_requested.emit(self.step, -1))
        layout.addWidget(up_btn)
        
        # Move down button
        down_btn = QPushButton("▼")
        down_btn.setFixedSize(20, 20)
        down_btn.setToolTip("Move down")
        down_btn.setStyleSheet(btn_style)
        down_btn.clicked.connect(lambda: self.move_requested.emit(self.step, 1))
        layout.addWidget(down_btn)
        
        dup_btn = QPushButton("📋")
        dup_btn.setFixedSize(22, 22)
        dup_btn.setToolTip("Duplicate (Ctrl+D)")
        dup_btn.setStyleSheet(btn_style)
        dup_btn.clicked.connect(lambda: self.duplicate_requested.emit(self.step))
        layout.addWidget(dup_btn)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(22, 22)
        edit_btn.setToolTip("Edit (Enter)")
        edit_btn.setStyleSheet(btn_style)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.step))
        layout.addWidget(edit_btn)
        
        del_btn = QPushButton("🗑️")
        del_btn.setFixedSize(22, 22)
        del_btn.setToolTip("Delete (Del)")
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {self.colors['error']};
            }}
        """)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.step.id))
        layout.addWidget(del_btn)
    
    def _update_style(self) -> None:
        border_color = self.colors['accent'] if self._is_selected else self.colors['border']
        self.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['surface']};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background: {self.colors['bg_alt']};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
    
    def set_selected(self, selected: bool) -> None:
        self._is_selected = selected
        self._update_style()
    
    def _get_preview(self) -> str:
        p = self.step.params
        if self.step.type == "open_app":
            path = p.get("path", "")
            return path.split("\\")[-1] if path else "No app"
        elif self.step.type == "open_url":
            url = p.get("url", "https://")
            return url[:30] + "..." if len(url) > 30 else url
        elif self.step.type == "delay":
            return f"Wait {p.get('seconds', 1)}s"
        elif self.step.type == "click":
            return f"Click ({p.get('x', 0)}, {p.get('y', 0)})"
        elif self.step.type == "type_text":
            text = p.get("text", "")[:20]
            return text + "..." if len(p.get("text", "")) > 20 else text or "No text"
        elif self.step.type == "hotkey":
            return p.get("keys", "No hotkey")
        elif self.step.type == "paste_history":
            idx = p.get("history_index", 0)
            return ["Last", "2nd", "3rd", "4th", "5th"][min(idx, 4)]
        elif self.step.type == "jiggle":
            dur = p.get("duration", 60)
            return f"{dur}s - {p.get('pattern', 'Natural')}"
        return "Configure..."
    
    def mouseDoubleClickEvent(self, event) -> None:
        self.edit_requested.emit(self.step)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self.selected.emit(self.step)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        if self._drag_start_pos and (event.pos() - self._drag_start_pos).manhattanLength() > 10:
            self.drag_started.emit(self.step)
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.step.id)
            drag.setMimeData(mime)
            drag.exec(Qt.MoveAction)
            self._drag_start_pos = None
    
    def mouseReleaseEvent(self, event) -> None:
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)
    
    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # Visual feedback
            self.setStyleSheet(f"""
                QFrame {{
                    background: {self.colors['accent']}20;
                    border: 2px dashed {self.colors['accent']};
                    border-radius: 6px;
                }}
                QLabel {{ background: transparent; border: none; }}
            """)
    
    def dragLeaveEvent(self, event) -> None:
        self._update_style()
    
    def dropEvent(self, event) -> None:
        self._update_style()
        if hasattr(self, 'drop_handler') and hasattr(self, 'drop_index'):
            self.drop_handler(event, self.drop_index)
    
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            self.delete_requested.emit(self.step.id)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.edit_requested.emit(self.step)
        else:
            super().keyPressEvent(event)


# ============================================================================
# STEP EDIT DIALOG
# ============================================================================
class StepEditDialog(QDialog):
    """Dialog for editing step parameters."""
    
    def __init__(self, step: WorkflowStep, colors: dict, parent=None) -> None:
        super().__init__(parent)
        self.step = step
        self.colors = colors
        self.setWindowTitle(f"Edit: {step.display_name}")
        self.setMinimumWidth(380)
        self.setModal(True)
        self._build_ui()
    
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel(f"{self.step.icon} {self.step.display_name}"))
        header.addStretch()
        layout.addLayout(header)
        
        # Form
        form = QFormLayout()
        form.setSpacing(8)
        
        if self.step.type == "open_app":
            self.app_label = QLabel(self.step.params.get("path", "No app selected"))
            self.app_label.setWordWrap(True)
            form.addRow("App:", self.app_label)
            
            btn = QPushButton("📂 Select Application")
            btn.clicked.connect(self._pick_app)
            form.addRow("", btn)
            
        elif self.step.type == "open_url":
            self.url_input = QLineEdit(self.step.params.get("url", "https://"))
            form.addRow("URL:", self.url_input)
            
        elif self.step.type == "delay":
            self.delay_spin = QDoubleSpinBox()
            self.delay_spin.setRange(0.1, 3600)
            self.delay_spin.setValue(self.step.params.get("seconds", 1.0))
            self.delay_spin.setSuffix(" seconds")
            form.addRow("Duration:", self.delay_spin)
            
        elif self.step.type == "click":
            coord = QHBoxLayout()
            self.x_spin = QSpinBox()
            self.x_spin.setRange(0, 9999)
            self.x_spin.setValue(self.step.params.get("x", 0))
            coord.addWidget(QLabel("X:"))
            coord.addWidget(self.x_spin)
            
            self.y_spin = QSpinBox()
            self.y_spin.setRange(0, 9999)
            self.y_spin.setValue(self.step.params.get("y", 0))
            coord.addWidget(QLabel("Y:"))
            coord.addWidget(self.y_spin)
            form.addRow("Position:", coord)
            
            pick_btn = QPushButton("🎯 Pick from Screen")
            pick_btn.clicked.connect(self._pick_coordinates)
            form.addRow("", pick_btn)
            
        elif self.step.type == "type_text":
            self.text_edit = QTextEdit()
            self.text_edit.setPlainText(self.step.params.get("text", ""))
            self.text_edit.setMaximumHeight(80)
            form.addRow("Text:", self.text_edit)
            
        elif self.step.type == "hotkey":
            self.hotkey_input = QLineEdit(self.step.params.get("keys", ""))
            self.hotkey_input.setPlaceholderText("ctrl+shift+s")
            form.addRow("Hotkey:", self.hotkey_input)
            
        elif self.step.type == "paste_history":
            self.history_combo = QComboBox()
            self.history_combo.addItems(["Last copied", "2nd last", "3rd last", "4th last", "5th last"])
            self.history_combo.setCurrentIndex(self.step.params.get("history_index", 0))
            form.addRow("Item:", self.history_combo)
            
        elif self.step.type == "jiggle":
            # Duration
            self.jiggle_duration = QSpinBox()
            self.jiggle_duration.setRange(5, 36000)
            self.jiggle_duration.setValue(self.step.params.get("duration", 60))
            self.jiggle_duration.setSuffix(" seconds")
            form.addRow("Duration:", self.jiggle_duration)
            
            # Pattern
            self.jiggle_pattern = QComboBox()
            self.jiggle_pattern.addItems(["Natural", "Invisible", "Subtle", "Circle", "Random"])
            current = self.step.params.get("pattern", "Natural")
            idx = self.jiggle_pattern.findText(current)
            self.jiggle_pattern.setCurrentIndex(idx if idx >= 0 else 0)
            form.addRow("Pattern:", self.jiggle_pattern)
            
            # Interval
            self.jiggle_interval = QSpinBox()
            self.jiggle_interval.setRange(1, 120)
            self.jiggle_interval.setValue(self.step.params.get("interval", 30))
            self.jiggle_interval.setSuffix(" sec interval")
            form.addRow("Move every:", self.jiggle_interval)
            
            # Track mouse
            self.track_mouse = QCheckBox("Track real mouse movement")
            self.track_mouse.setChecked(self.step.params.get("track_mouse", True))
            self.track_mouse.setToolTip("Count your natural mouse movements as activity")
            form.addRow("", self.track_mouse)
            
            # Schedule options
            self.use_schedule = QCheckBox("Use schedule")
            self.use_schedule.setChecked(self.step.params.get("use_schedule", False))
            form.addRow("", self.use_schedule)
            
            sched_layout = QHBoxLayout()
            sched_layout.addWidget(QLabel("Start:"))
            self.start_time = QTimeEdit()
            self.start_time.setDisplayFormat("HH:mm")
            start = self.step.params.get("start_time", "09:00")
            self.start_time.setTime(self.start_time.time().fromString(start, "HH:mm"))
            sched_layout.addWidget(self.start_time)
            
            sched_layout.addWidget(QLabel("End:"))
            self.end_time = QTimeEdit()
            self.end_time.setDisplayFormat("HH:mm")
            end = self.step.params.get("end_time", "17:00")
            self.end_time.setTime(self.end_time.time().fromString(end, "HH:mm"))
            sched_layout.addWidget(self.end_time)
            form.addRow("Schedule:", sched_layout)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _pick_app(self) -> None:
        result = AppPickerDialog.get_app(self)
        if result:
            _, path = result
            self.step.params["path"] = path
            self.app_label.setText(path)
    
    def _pick_coordinates(self) -> None:
        self.hide()
        QTimer.singleShot(200, self._do_pick)
    
    def _do_pick(self) -> None:
        picker = CoordinatePicker()
        if picker.exec() == QDialog.Accepted:
            x, y = picker.get_coordinates()
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
        self.show()
    
    def get_params(self) -> Dict[str, Any]:
        params = dict(self.step.params)
        
        if self.step.type == "open_url":
            params["url"] = self.url_input.text()
        elif self.step.type == "delay":
            params["seconds"] = self.delay_spin.value()
        elif self.step.type == "click":
            params["x"] = self.x_spin.value()
            params["y"] = self.y_spin.value()
        elif self.step.type == "type_text":
            params["text"] = self.text_edit.toPlainText()
        elif self.step.type == "hotkey":
            params["keys"] = self.hotkey_input.text()
        elif self.step.type == "paste_history":
            params["history_index"] = self.history_combo.currentIndex()
        elif self.step.type == "jiggle":
            params["duration"] = self.jiggle_duration.value()
            params["pattern"] = self.jiggle_pattern.currentText()
            params["interval"] = self.jiggle_interval.value()
            params["track_mouse"] = self.track_mouse.isChecked()
            params["use_schedule"] = self.use_schedule.isChecked()
            params["start_time"] = self.start_time.time().toString("HH:mm")
            params["end_time"] = self.end_time.time().toString("HH:mm")
        
        return params


# ============================================================================
# ADD STEP DIALOG
# ============================================================================
class AddStepDialog(QDialog):
    """Dialog to choose step type."""
    
    step_selected = Signal(str)
    
    def __init__(self, colors: dict, parent=None) -> None:
        super().__init__(parent)
        self.colors = colors
        self.setWindowTitle("Add Step")
        self.setMinimumSize(320, 380)
        self.setModal(True)
        self._build_ui()
    
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search...")
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)
        
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._select_item)
        layout.addWidget(self.list, 1)
        
        self._populate()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("Add")
        add_btn.setProperty("primary", True)
        add_btn.clicked.connect(self._select_current)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
    
    def _populate(self, filter_text: str = "") -> None:
        self.list.clear()
        for type_id, info in STEP_TYPES.items():
            if filter_text and filter_text.lower() not in info["name"].lower():
                continue
            item = QListWidgetItem(f"{info['icon']}  {info['name']}")
            item.setData(Qt.UserRole, type_id)
            item.setToolTip(info["desc"])
            self.list.addItem(item)
    
    def _filter(self, text: str) -> None:
        self._populate(text)
    
    def _select_item(self, item: QListWidgetItem) -> None:
        self.step_selected.emit(item.data(Qt.UserRole))
        self.accept()
    
    def _select_current(self) -> None:
        item = self.list.currentItem()
        if item:
            self._select_item(item)


# ============================================================================
# MINI MAP
# ============================================================================
class MiniMap(QWidget):
    """Mini-map for workflow overview."""
    
    scroll_requested = Signal(float)
    
    def __init__(self, colors: dict, parent=None) -> None:
        super().__init__(parent)
        self.colors = colors
        self.steps: List[WorkflowStep] = []
        self.viewport_pos = 0.0
        self.viewport_ratio = 0.3
        self.setFixedWidth(50)
        self.setMinimumHeight(80)
    
    def set_steps(self, steps: List[WorkflowStep]) -> None:
        self.steps = steps
        self.update()
    
    def set_viewport(self, pos: float, ratio: float) -> None:
        self.viewport_pos = max(0, min(1, pos))
        self.viewport_ratio = max(0.1, min(1, ratio))
        self.update()
    
    def paintEvent(self, event) -> None:
        if not self.steps:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(self.colors['surface']))
        painter.setPen(QPen(QColor(self.colors['border']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        margin = 4
        h = self.height() - margin * 2
        step_h = min(6, h // max(len(self.steps), 1))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self.colors['accent']))
        
        for i in range(len(self.steps)):
            y = margin + i * (step_h + 2)
            if y + step_h > self.height() - margin:
                break
            painter.drawRoundedRect(margin, y, self.width() - margin * 2, step_h, 2, 2)
        
        # Viewport
        if len(self.steps) > 5:
            vp_h = max(15, h * self.viewport_ratio)
            vp_y = margin + (h - vp_h) * self.viewport_pos
            painter.setBrush(QColor(self.colors['accent'] + "40"))
            painter.setPen(QPen(QColor(self.colors['accent']), 1))
            painter.drawRect(1, int(vp_y), self.width() - 2, int(vp_h))
    
    def mousePressEvent(self, event) -> None:
        self.scroll_requested.emit(event.pos().y() / self.height())
    
    def mouseMoveEvent(self, event) -> None:
        self.scroll_requested.emit(event.pos().y() / self.height())


# ============================================================================
# MAIN WORKFLOW BUILDER VIEW
# ============================================================================
class WorkflowBuilderView(QWidget):
    """Visual workflow builder."""

    def __init__(
        self,
        config_manager: ConfigManager,
        theme_manager: ThemeManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.colors = theme_manager.current.colors
        self.steps: List[WorkflowStep] = []
        self._editing_action_id: Optional[str] = None
        self._selected_step: Optional[WorkflowStep] = None
        self._drag_source_idx: Optional[int] = None
        self._palette_collapsed = False
        
        self._build_ui()
        self._setup_shortcuts()
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        del_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        del_shortcut.activated.connect(self._delete_selected)
        
        dup_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        dup_shortcut.activated.connect(self._duplicate_selected)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        header.setSpacing(8)
        
        title = QLabel("🔧 Workflow Builder")
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        
        self.preview_btn = QPushButton("▶ Preview")
        self.preview_btn.clicked.connect(self._preview_workflow)
        header.addWidget(self.preview_btn)
        
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.clicked.connect(self._clear_all)
        header.addWidget(clear_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setProperty("primary", True)
        self.save_btn.clicked.connect(self._save_action)
        header.addWidget(self.save_btn)
        
        layout.addLayout(header)

        # Details row
        details = QHBoxLayout()
        details.setSpacing(8)
        
        details.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Workflow")
        self.name_input.setMaximumWidth(180)
        details.addWidget(self.name_input)
        
        details.addWidget(QLabel("Hotkey:"))
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("Ctrl+Shift+1")
        self.hotkey_input.setMaximumWidth(100)
        details.addWidget(self.hotkey_input)
        
        details.addStretch()
        
        self.step_count = QLabel("0 steps")
        self.step_count.setStyleSheet(f"color: {self.colors['text_muted']};")
        details.addWidget(self.step_count)
        
        layout.addLayout(details)

        # Main content
        content = QHBoxLayout()
        content.setSpacing(8)
        
        # Canvas
        canvas = QWidget()
        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"border: 1px dashed {self.colors['border']}; border-radius: 6px;")
        
        self.steps_widget = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_widget)
        self.steps_layout.setContentsMargins(10, 10, 10, 10)
        self.steps_layout.setSpacing(6)
        self.steps_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.steps_widget)
        self.scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        canvas_layout.addWidget(self.scroll, 1)
        
        # Add button
        self.add_btn = QPushButton("+ Add Step")
        self.add_btn.setMinimumHeight(32)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px dashed {self.colors['border']};
                border-radius: 5px;
                color: {self.colors['text_muted']};
            }}
            QPushButton:hover {{
                background: {self.colors['accent']};
                color: white;
                border-color: {self.colors['accent']};
            }}
        """)
        self.add_btn.clicked.connect(self._add_step_dialog)
        canvas_layout.addWidget(self.add_btn)
        
        content.addWidget(canvas, 1)
        
        # Minimap
        self.minimap = MiniMap(self.colors)
        self.minimap.scroll_requested.connect(self._on_minimap_scroll)
        self.minimap.hide()
        content.addWidget(self.minimap)
        
        # Quick Add panel - wider for readability
        self.palette = QWidget()
        self.palette.setMinimumWidth(180)
        self.palette.setMaximumWidth(200)
        pal_layout = QVBoxLayout(self.palette)
        pal_layout.setContentsMargins(0, 0, 0, 0)
        pal_layout.setSpacing(4)
        
        # Header with title
        pal_header = QHBoxLayout()
        pal_title = QLabel("⚡ Quick Add")
        pal_title.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {self.colors['text']};")
        pal_header.addWidget(pal_title)
        pal_header.addStretch()
        
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setFixedSize(20, 20)
        self.collapse_btn.setStyleSheet(f"border: none; background: transparent; color: {self.colors['text_muted']};")
        self.collapse_btn.clicked.connect(self._toggle_palette)
        pal_header.addWidget(self.collapse_btn)
        pal_layout.addLayout(pal_header)
        
        # Buttons - larger and more readable
        self.pal_content = QWidget()
        pal_content_layout = QVBoxLayout(self.pal_content)
        pal_content_layout.setContentsMargins(0, 4, 0, 0)
        pal_content_layout.setSpacing(2)
        
        for type_id, info in STEP_TYPES.items():
            btn = QPushButton(f"{info['icon']}  {info['name']}")
            btn.setMinimumHeight(32)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.colors['surface']};
                    border: 1px solid {self.colors['border']};
                    border-radius: 6px;
                    padding: 6px 10px;
                    text-align: left;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {self.colors['accent']};
                    border-color: {self.colors['accent']};
                    color: white;
                }}
            """)
            btn.setToolTip(info['desc'])
            btn.clicked.connect(self._make_add_step_handler(type_id))
            pal_content_layout.addWidget(btn)
        
        pal_content_layout.addStretch()
        pal_layout.addWidget(self.pal_content)
        
        content.addWidget(self.palette)
        layout.addLayout(content, 1)
        
        self._refresh_canvas()

    def _make_add_step_handler(self, type_id: str):
        """Create a handler for adding a step type."""
        def handler():
            self._add_step(type_id)
        return handler

    def _toggle_palette(self) -> None:
        self._palette_collapsed = not self._palette_collapsed
        self.pal_content.setVisible(not self._palette_collapsed)
        self.collapse_btn.setText("▶" if self._palette_collapsed else "◀")
        if self._palette_collapsed:
            self.palette.setMinimumWidth(30)
            self.palette.setMaximumWidth(30)
        else:
            self.palette.setMinimumWidth(180)
            self.palette.setMaximumWidth(200)

    def _on_theme_changed(self, theme) -> None:
        self.colors = theme.colors
        self._refresh_canvas()

    def _on_scroll(self, value: int) -> None:
        sb = self.scroll.verticalScrollBar()
        if sb.maximum() > 0:
            self.minimap.set_viewport(value / sb.maximum(), sb.pageStep() / (sb.maximum() + sb.pageStep()))

    def _on_minimap_scroll(self, pos: float) -> None:
        sb = self.scroll.verticalScrollBar()
        sb.setValue(int(pos * sb.maximum()))

    def _add_step_dialog(self) -> None:
        dlg = AddStepDialog(self.colors, self)
        dlg.step_selected.connect(self._add_step)
        dlg.exec()

    def _add_step(self, step_type: str) -> None:
        step = WorkflowStep(type=step_type, params={})
        
        # Defaults
        defaults = {
            "open_url": {"url": "https://"},
            "delay": {"seconds": 1.0},
            "paste_history": {"history_index": 0},
            "jiggle": {"duration": 60, "pattern": "Natural", "interval": 30, "track_mouse": True},
        }
        step.params = defaults.get(step_type, {})
        
        self.steps.append(step)
        self._refresh_canvas()
        self._edit_step(step)

    def _edit_step(self, step: WorkflowStep) -> None:
        dlg = StepEditDialog(step, self.colors, self)
        if dlg.exec() == QDialog.Accepted:
            step.params = dlg.get_params()
            self._refresh_canvas()

    def _delete_step(self, step_id: str) -> None:
        self.steps = [s for s in self.steps if s.id != step_id]
        self._selected_step = None
        self._refresh_canvas()

    def _delete_selected(self) -> None:
        if self._selected_step:
            self._delete_step(self._selected_step.id)

    def _duplicate_step(self, step: WorkflowStep) -> None:
        idx = next((i for i, s in enumerate(self.steps) if s.id == step.id), -1)
        if idx >= 0:
            self.steps.insert(idx + 1, step.clone())
            self._refresh_canvas()

    def _duplicate_selected(self) -> None:
        if self._selected_step:
            self._duplicate_step(self._selected_step)

    def _select_step(self, step: WorkflowStep) -> None:
        self._selected_step = step
        self._refresh_canvas()

    def _on_drag(self, step: WorkflowStep) -> None:
        self._drag_source_idx = next((i for i, s in enumerate(self.steps) if s.id == step.id), None)

    def _refresh_canvas(self) -> None:
        # Clear
        while self.steps_layout.count():
            item = self.steps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.step_count.setText(f"{len(self.steps)} step{'s' if len(self.steps) != 1 else ''}")
        self.minimap.setVisible(len(self.steps) > 5)
        self.minimap.set_steps(self.steps)
        
        if not self.steps:
            empty = QLabel("No steps yet.\nClick '+ Add Step' or use Quick Add →")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {self.colors['text_muted']}; padding: 30px; font-size: 11px;")
            self.steps_layout.addWidget(empty)
        else:
            for i, step in enumerate(self.steps):
                if i > 0:
                    arrow = QLabel("↓")
                    arrow.setAlignment(Qt.AlignCenter)
                    arrow.setStyleSheet(f"color: {self.colors['text_muted']}; font-size: 12px;")
                    arrow.setFixedHeight(12)
                    self.steps_layout.addWidget(arrow)
                
                block = StepBlock(step, i, self.colors)
                block.set_selected(self._selected_step and self._selected_step.id == step.id)
                block.edit_requested.connect(self._edit_step)
                block.delete_requested.connect(self._delete_step)
                block.duplicate_requested.connect(self._duplicate_step)
                block.drag_started.connect(self._on_drag)
                block.selected.connect(self._select_step)
                block.move_requested.connect(self._move_step)
                
                # Store index for drop handling
                block.drop_index = i
                block.drop_handler = self._handle_drop
                
                self.steps_layout.addWidget(block)
        
        self.steps_layout.addStretch()

    def _move_step(self, step: WorkflowStep, direction: int) -> None:
        """Move a step up (-1) or down (+1)."""
        idx = next((i for i, s in enumerate(self.steps) if s.id == step.id), -1)
        if idx < 0:
            return
        
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.steps):
            return
        
        # Swap
        self.steps[idx], self.steps[new_idx] = self.steps[new_idx], self.steps[idx]
        self._refresh_canvas()

    def _handle_drop(self, event, target_idx: int) -> None:
        if self._drag_source_idx is None or self._drag_source_idx == target_idx:
            return
        
        step = self.steps.pop(self._drag_source_idx)
        if target_idx > self._drag_source_idx:
            target_idx -= 1
        self.steps.insert(target_idx, step)
        self._drag_source_idx = None
        self._refresh_canvas()
        event.acceptProposedAction()

    def _preview_workflow(self) -> None:
        if not self.steps:
            QMessageBox.information(self, "Preview", "Add some steps first!")
            return
        
        steps_str = "\n".join([f"  {i+1}. {s.display_name}" for i, s in enumerate(self.steps)])
        if QMessageBox.question(self, "Preview", f"Run workflow?\n\n{steps_str}") != QMessageBox.Yes:
            return
        
        self._run_preview()

    def _run_preview(self) -> None:
        from ...actions.steps import step_from_def, StepContext, CancelToken
        from ...actions.results import RunResult
        
        result = RunResult()
        ctx = StepContext(config=self.config_manager, inputs={}, cancel=CancelToken())
        
        try:
            for i, step in enumerate(self.steps):
                executor = step_from_def(step.type, step.params)
                if executor:
                    result.add_log("INFO", f"Step {i+1}: {step.display_name}")
                    QApplication.processEvents()
                    executor.run(ctx, result)
            
            QMessageBox.information(self, "Done", "Workflow completed!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {str(e)}")

    def _clear_all(self) -> None:
        if self.steps and QMessageBox.question(self, "Clear", "Clear all steps?") != QMessageBox.Yes:
            return
        
        self.steps = []
        self.name_input.clear()
        self.hotkey_input.clear()
        self._editing_action_id = None
        self.save_btn.setText("💾 Save")
        self._refresh_canvas()

    def _save_action(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Enter a name.")
            return
        if not self.steps:
            QMessageBox.warning(self, "Error", "Add at least one step.")
            return
        
        from ...config.models import ActionDef, StepDef
        
        step_defs = [StepDef(type=s.type, params=s.params) for s in self.steps]
        
        if self._editing_action_id:
            for action in self.config_manager.actions.actions:
                if action.id == self._editing_action_id:
                    action.name = name
                    action.hotkey = self.hotkey_input.text().strip() or None
                    action.steps = step_defs
                    action.description = f"Workflow: {len(self.steps)} steps"
                    break
            self.config_manager.save_all()
            QMessageBox.information(self, "Updated", f"'{name}' updated!")
        else:
            new_action = ActionDef(
                id=str(uuid.uuid4())[:8],
                name=name,
                description=f"Workflow: {len(self.steps)} steps",
                hotkey=self.hotkey_input.text().strip() or None,
                tags=["workflow"],
                steps=step_defs,
            )
            self.config_manager.actions.actions.append(new_action)
            self.config_manager.save_all()
            QMessageBox.information(self, "Saved", f"'{name}' saved!")
        
        # Reset without confirmation
        self.steps = []
        self.name_input.clear()
        self.hotkey_input.clear()
        self._editing_action_id = None
        self.save_btn.setText("💾 Save")
        self._refresh_canvas()
        
        main = self.window()
        if hasattr(main, "action_view"):
            main.action_view.refresh()
        if hasattr(main, "refresh_hotkeys"):
            main.refresh_hotkeys()

    def load_action(self, action) -> None:
        self.steps = []
        self.name_input.setText(action.name)
        self.hotkey_input.setText(action.hotkey or "")
        self._editing_action_id = action.id
        
        for step_def in action.steps:
            self.steps.append(WorkflowStep(type=step_def.type, params=dict(step_def.params) if step_def.params else {}))
        
        self._refresh_canvas()
        self.save_btn.setText("💾 Update")

    def filter_items(self, text: str) -> None:
        pass
