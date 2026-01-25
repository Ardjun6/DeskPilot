"""Action Recorder - record mouse and keyboard to create actions."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
)

import pyautogui
from pynput import mouse, keyboard

from ...config.config_manager import ConfigManager
from ..theme_manager import ThemeManager
from ..widgets.grid_layout import GridCanvas


@dataclass
class RecordedAction:
    """A single recorded action."""
    action_type: str  # click, move, key, type
    timestamp: float
    data: dict = field(default_factory=dict)
    
    @property
    def display_text(self) -> str:
        if self.action_type == "click":
            btn = self.data.get("button", "left")
            x, y = self.data.get("x", 0), self.data.get("y", 0)
            return f"🖱️ Click ({btn}) at ({x}, {y})"
        elif self.action_type == "key":
            key = self.data.get("key", "")
            return f"⌨️ Press key: {key}"
        elif self.action_type == "hotkey":
            keys = self.data.get("keys", [])
            return f"⌨️ Hotkey: {'+'.join(keys)}"
        elif self.action_type == "delay":
            secs = self.data.get("seconds", 0)
            return f"⏱️ Wait {secs:.1f}s"
        return f"❓ {self.action_type}"


class RecorderThread(QThread):
    """Background thread for recording mouse and keyboard."""
    
    action_recorded = Signal(object)  # RecordedAction
    recording_stopped = Signal()
    
    def __init__(self, record_mouse: bool = True, record_keyboard: bool = True) -> None:
        super().__init__()
        self.record_mouse = record_mouse
        self.record_keyboard = record_keyboard
        self._running = False
        self._last_action_time = 0
        self._current_modifiers = set()
        self._mouse_listener = None
        self._keyboard_listener = None

    def run(self) -> None:
        self._running = True
        self._last_action_time = time.time()
        
        if self.record_mouse:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click
            )
            self._mouse_listener.start()
        
        if self.record_keyboard:
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._keyboard_listener.start()
        
        # Keep thread alive
        while self._running:
            time.sleep(0.1)
        
        # Cleanup
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        
        self.recording_stopped.emit()

    def stop(self) -> None:
        self._running = False

    def _add_delay_if_needed(self) -> None:
        """Add a delay action if significant time has passed."""
        now = time.time()
        delay = now - self._last_action_time
        if delay > 0.5:  # More than 0.5 seconds
            action = RecordedAction(
                action_type="delay",
                timestamp=self._last_action_time,
                data={"seconds": round(delay, 1)}
            )
            self.action_recorded.emit(action)
        self._last_action_time = now

    def _on_mouse_click(self, x, y, button, pressed) -> None:
        if not self._running or not pressed:
            return
        
        self._add_delay_if_needed()
        
        btn_name = "left" if button == mouse.Button.left else "right"
        action = RecordedAction(
            action_type="click",
            timestamp=time.time(),
            data={"x": x, "y": y, "button": btn_name}
        )
        self.action_recorded.emit(action)

    def _on_key_press(self, key) -> None:
        if not self._running:
            return
        
        # Track modifiers
        try:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._current_modifiers.add("ctrl")
            elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
                self._current_modifiers.add("alt")
            elif key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
                self._current_modifiers.add("shift")
            elif key == keyboard.Key.cmd:
                self._current_modifiers.add("win")
            else:
                self._add_delay_if_needed()
                
                # Get key name
                if hasattr(key, 'char') and key.char:
                    key_name = key.char
                else:
                    key_name = str(key).replace("Key.", "")
                
                if self._current_modifiers:
                    # It's a hotkey combination
                    keys = list(self._current_modifiers) + [key_name]
                    action = RecordedAction(
                        action_type="hotkey",
                        timestamp=time.time(),
                        data={"keys": keys}
                    )
                else:
                    action = RecordedAction(
                        action_type="key",
                        timestamp=time.time(),
                        data={"key": key_name}
                    )
                self.action_recorded.emit(action)
        except Exception:
            pass

    def _on_key_release(self, key) -> None:
        try:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self._current_modifiers.discard("ctrl")
            elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
                self._current_modifiers.discard("alt")
            elif key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
                self._current_modifiers.discard("shift")
            elif key == keyboard.Key.cmd:
                self._current_modifiers.discard("win")
        except Exception:
            pass


class RecorderView(QWidget):
    """View for recording mouse and keyboard actions."""

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
        self.recorded_actions: List[RecordedAction] = []
        self.recorder_thread: Optional[RecorderThread] = None
        self.is_recording = False
        
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        grid = GridCanvas()

        # Recording controls
        control_cell = grid.add_cell(0, 0, row_span=1, col_span=2, title="🎬 Action Recorder")
        
        desc = QLabel(
            "Record your mouse clicks and keyboard presses to automatically create an action. "
            "Press F9 or click Stop to finish recording."
        )
        desc.setObjectName("ActionDesc")
        desc.setWordWrap(True)
        control_cell.layout.addWidget(desc)
        
        control_cell.layout.addSpacing(12)
        
        # Options
        options = QHBoxLayout()
        
        self.mouse_check = QCheckBox("Record mouse clicks")
        self.mouse_check.setChecked(True)
        options.addWidget(self.mouse_check)
        
        self.keyboard_check = QCheckBox("Record keyboard")
        self.keyboard_check.setChecked(True)
        options.addWidget(self.keyboard_check)
        
        options.addStretch()
        
        options.addWidget(QLabel("Countdown:"))
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(0, 10)
        self.countdown_spin.setValue(3)
        self.countdown_spin.setSuffix(" sec")
        options.addWidget(self.countdown_spin)
        
        control_cell.layout.addLayout(options)
        
        control_cell.layout.addSpacing(12)
        
        # Status
        self.status_frame = QFrame()
        self.status_frame.setProperty("card", True)
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setContentsMargins(20, 16, 20, 16)
        
        self.status_icon = QLabel("⏹️")
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setStyleSheet("font-size: 36px;")
        status_layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("Ready to record")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        status_layout.addWidget(self.status_label)
        
        self.action_count = QLabel("0 actions recorded")
        self.action_count.setAlignment(Qt.AlignCenter)
        self.action_count.setObjectName("ActionDesc")
        status_layout.addWidget(self.action_count)
        
        control_cell.layout.addWidget(self.status_frame)
        
        control_cell.layout.addSpacing(12)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("🔴 Start Recording")
        self.record_btn.setProperty("primary", True)
        self.record_btn.setMinimumHeight(40)
        self.record_btn.clicked.connect(self._toggle_recording)
        btn_layout.addWidget(self.record_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self._clear_recording)
        btn_layout.addWidget(self.clear_btn)
        
        control_cell.layout.addLayout(btn_layout)

        # Recorded actions list
        list_cell = grid.add_cell(1, 0, row_span=2, col_span=2, title="📝 Recorded Steps")
        
        self.action_list = QListWidget()
        self.action_list.setStyleSheet(f"""
            QListWidget {{
                background: {self.colors['surface']};
                border: 1px solid {self.colors['border_soft']};
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {self.colors['border_soft']};
            }}
        """)
        list_cell.layout.addWidget(self.action_list)
        
        # Delete selected
        del_btn = QPushButton("🗑️ Delete Selected Step")
        del_btn.clicked.connect(self._delete_selected)
        list_cell.layout.addWidget(del_btn)

        # Save panel
        save_cell = grid.add_cell(0, 2, row_span=3, col_span=1, title="💾 Save Action")
        
        save_cell.layout.addWidget(QLabel("Action Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Recorded Action")
        save_cell.layout.addWidget(self.name_input)
        
        save_cell.layout.addSpacing(8)
        
        save_cell.layout.addWidget(QLabel("Description:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("What does this do?")
        save_cell.layout.addWidget(self.desc_input)
        
        save_cell.layout.addSpacing(8)
        
        save_cell.layout.addWidget(QLabel("Hotkey:"))
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("Ctrl+Shift+R")
        save_cell.layout.addWidget(self.hotkey_input)
        
        save_cell.layout.addSpacing(16)
        
        self.save_btn = QPushButton("💾 Save as Action")
        self.save_btn.setProperty("primary", True)
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._save_action)
        save_cell.layout.addWidget(self.save_btn)
        
        save_cell.layout.addStretch()
        
        # Tips
        tips = [
            "💡 Tips:",
            "",
            "• Use countdown to switch windows",
            "• Press F9 to stop recording",
            "• Delays are auto-detected",
            "• Delete unwanted steps",
            "• Test before saving",
        ]
        for tip in tips:
            if tip:
                lbl = QLabel(tip)
                lbl.setObjectName("ActionDesc")
                save_cell.layout.addWidget(lbl)
            else:
                save_cell.layout.addSpacing(4)

        layout.addWidget(grid)

    def _toggle_recording(self) -> None:
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        countdown = self.countdown_spin.value()
        
        if countdown > 0:
            self.status_icon.setText("⏱️")
            self.status_label.setText(f"Starting in {countdown}...")
            self.record_btn.setEnabled(False)
            
            # Countdown timer
            self._countdown_remaining = countdown
            self._countdown_timer = QTimer(self)
            self._countdown_timer.timeout.connect(self._countdown_tick)
            self._countdown_timer.start(1000)
        else:
            self._actually_start_recording()

    def _countdown_tick(self) -> None:
        self._countdown_remaining -= 1
        if self._countdown_remaining > 0:
            self.status_label.setText(f"Starting in {self._countdown_remaining}...")
        else:
            self._countdown_timer.stop()
            self._actually_start_recording()

    def _actually_start_recording(self) -> None:
        self.is_recording = True
        self.recorded_actions = []
        self.action_list.clear()
        
        self.status_icon.setText("🔴")
        self.status_label.setText("Recording...")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #ef4444;")
        self.record_btn.setText("⏹️ Stop Recording")
        self.record_btn.setEnabled(True)
        self.action_count.setText("0 actions recorded")
        
        # Start recorder thread
        self.recorder_thread = RecorderThread(
            record_mouse=self.mouse_check.isChecked(),
            record_keyboard=self.keyboard_check.isChecked()
        )
        self.recorder_thread.action_recorded.connect(self._on_action_recorded)
        self.recorder_thread.recording_stopped.connect(self._on_recording_stopped)
        self.recorder_thread.start()

    def _stop_recording(self) -> None:
        if self.recorder_thread:
            self.recorder_thread.stop()

    def _on_action_recorded(self, action: RecordedAction) -> None:
        self.recorded_actions.append(action)
        
        item = QListWidgetItem(action.display_text)
        self.action_list.addItem(item)
        self.action_list.scrollToBottom()
        
        self.action_count.setText(f"{len(self.recorded_actions)} actions recorded")

    def _on_recording_stopped(self) -> None:
        self.is_recording = False
        self.recorder_thread = None
        
        self.status_icon.setText("✅")
        self.status_label.setText("Recording complete")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.record_btn.setText("🔴 Start Recording")

    def _clear_recording(self) -> None:
        self.recorded_actions = []
        self.action_list.clear()
        self.action_count.setText("0 actions recorded")

    def _delete_selected(self) -> None:
        row = self.action_list.currentRow()
        if row >= 0:
            self.action_list.takeItem(row)
            self.recorded_actions.pop(row)
            self.action_count.setText(f"{len(self.recorded_actions)} actions recorded")

    def _save_action(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter an action name.")
            return
        
        if not self.recorded_actions:
            QMessageBox.warning(self, "Error", "No actions recorded.")
            return
        
        # Convert recorded actions to steps
        steps = []
        for action in self.recorded_actions:
            if action.action_type == "click":
                steps.append({
                    "type": "click",
                    "params": {"x": action.data["x"], "y": action.data["y"]}
                })
            elif action.action_type == "key":
                steps.append({
                    "type": "type_text",
                    "params": {"text": action.data.get("key", "")}
                })
            elif action.action_type == "hotkey":
                keys = action.data.get("keys", [])
                steps.append({
                    "type": "hotkey",
                    "params": {"keys": keys}
                })
            elif action.action_type == "delay":
                steps.append({
                    "type": "delay",
                    "params": {"seconds": action.data.get("seconds", 1)}
                })
        
        # Create action
        from ...config.models import ActionDef, StepDef
        
        action_id = str(uuid.uuid4())[:8]
        step_defs = [StepDef(**s) for s in steps]
        
        new_action = ActionDef(
            id=action_id,
            name=name,
            description=self.desc_input.text().strip(),
            hotkey=self.hotkey_input.text().strip() or None,
            tags=["recorded"],
            steps=step_defs,
        )
        
        self.config_manager.actions.actions.append(new_action)
        self.config_manager.save_all()
        
        QMessageBox.information(
            self, "Saved",
            f"Action '{name}' saved with {len(steps)} steps!\n\nGo to Actions tab to run it."
        )
        
        # Clear
        self._clear_recording()
        self.name_input.clear()
        self.desc_input.clear()
        self.hotkey_input.clear()
        
        # Refresh main window
        main = self.window()
        if hasattr(main, "action_view"):
            main.action_view.refresh()
        if hasattr(main, "refresh_hotkeys"):
            main.refresh_hotkeys()

    def filter_items(self, text: str) -> None:
        pass

    def closeEvent(self, event) -> None:
        if self.recorder_thread:
            self.recorder_thread.stop()
        super().closeEvent(event)
