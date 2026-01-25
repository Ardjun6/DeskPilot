"""Jiggle View - Mouse jiggler with schedule, caffeine mode, and stats."""
from __future__ import annotations

import random
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QFrame,
)

import pyautogui

from ..widgets.grid_layout import GridCanvas


class JiggleView(QWidget):
    """Advanced mouse jiggler with schedule, caffeine mode, and statistics."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.is_running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._do_jiggle)
        self.schedule_timer = QTimer(self)
        self.schedule_timer.timeout.connect(self._check_schedule)
        self.schedule_timer.start(60000)
        
        self.jiggle_count = 0
        self.session_start: Optional[datetime] = None
        self.total_sessions = 0
        self.total_jiggles = 0
        self.total_minutes = 0
        
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        grid = GridCanvas()

        # Main control
        control_cell = grid.add_cell(0, 0, row_span=2, col_span=2, title="🖱️ Mouse Jiggler")

        desc = QLabel("Keeps your PC awake. Perfect for staying 'online' during work.")
        desc.setObjectName("ActionDesc")
        desc.setWordWrap(True)
        control_cell.layout.addWidget(desc)
        control_cell.layout.addSpacing(8)

        # Status
        self.status_frame = QFrame()
        self.status_frame.setProperty("card", True)
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setContentsMargins(20, 12, 20, 12)
        
        self.status_icon = QLabel("💤")
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setStyleSheet("font-size: 40px;")
        status_layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("Inactive")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        status_layout.addWidget(self.status_label)
        
        self.session_time = QLabel("Session: --:--:--")
        self.session_time.setAlignment(Qt.AlignCenter)
        self.session_time.setObjectName("ActionDesc")
        status_layout.addWidget(self.session_time)
        
        self.jiggle_counter = QLabel("Jiggles: 0")
        self.jiggle_counter.setAlignment(Qt.AlignCenter)
        self.jiggle_counter.setObjectName("ActionDesc")
        status_layout.addWidget(self.jiggle_counter)
        
        control_cell.layout.addWidget(self.status_frame)
        control_cell.layout.addSpacing(8)

        # Controls
        controls = QHBoxLayout()
        controls.setSpacing(12)
        
        controls.addWidget(QLabel("Pattern:"))
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Subtle (1px)", "Circle", "Random", "Square", "Invisible"])
        controls.addWidget(self.pattern_combo)
        
        controls.addWidget(QLabel("Every:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 300)
        self.interval_spin.setValue(30)
        self.interval_spin.setSuffix("s")
        controls.addWidget(self.interval_spin)
        controls.addStretch()
        control_cell.layout.addLayout(controls)
        control_cell.layout.addSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setProperty("primary", True)
        self.start_btn.setMinimumHeight(36)
        
        self.stop_btn = QPushButton("✕ Stop")
        self.stop_btn.setMinimumHeight(36)
        self.stop_btn.setEnabled(False)
        
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        control_cell.layout.addLayout(btn_row)

        # Caffeine mode
        self.caffeine_check = QCheckBox("☕ Caffeine Mode (no visible movement)")
        control_cell.layout.addWidget(self.caffeine_check)
        control_cell.layout.addStretch()

        # Schedule
        schedule_cell = grid.add_cell(0, 2, row_span=1, col_span=1, title="📅 Schedule")
        
        self.schedule_check = QCheckBox("Auto start/stop")
        schedule_cell.layout.addWidget(self.schedule_check)
        schedule_cell.layout.addSpacing(4)
        
        time_row1 = QHBoxLayout()
        time_row1.addWidget(QLabel("Start:"))
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(9, 0))
        self.start_time.setDisplayFormat("HH:mm")
        time_row1.addWidget(self.start_time)
        schedule_cell.layout.addLayout(time_row1)
        
        time_row2 = QHBoxLayout()
        time_row2.addWidget(QLabel("End:"))
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(17, 0))
        self.end_time.setDisplayFormat("HH:mm")
        time_row2.addWidget(self.end_time)
        schedule_cell.layout.addLayout(time_row2)
        
        schedule_cell.layout.addSpacing(4)
        days_label = QLabel("Days:")
        days_label.setObjectName("ActionDesc")
        schedule_cell.layout.addWidget(days_label)
        
        self.day_checks = {}
        days_row = QHBoxLayout()
        for day in ["M", "T", "W", "Th", "F"]:
            cb = QCheckBox(day)
            cb.setChecked(True)
            self.day_checks[day] = cb
            days_row.addWidget(cb)
        schedule_cell.layout.addLayout(days_row)
        schedule_cell.layout.addStretch()

        # Stats
        stats_cell = grid.add_cell(1, 2, row_span=1, col_span=1, title="📊 Stats")
        
        self.stats_sessions = QLabel("Sessions: 0")
        self.stats_sessions.setObjectName("ActionDesc")
        stats_cell.layout.addWidget(self.stats_sessions)
        
        self.stats_jiggles = QLabel("Total jiggles: 0")
        self.stats_jiggles.setObjectName("ActionDesc")
        stats_cell.layout.addWidget(self.stats_jiggles)
        
        self.stats_uptime = QLabel("Uptime: 0h 0m")
        self.stats_uptime.setObjectName("ActionDesc")
        stats_cell.layout.addWidget(self.stats_uptime)
        
        stats_cell.layout.addSpacing(8)
        reset_btn = QPushButton("Reset Stats")
        reset_btn.clicked.connect(self._reset_stats)
        stats_cell.layout.addWidget(reset_btn)
        stats_cell.layout.addStretch()

        layout.addWidget(grid)
        
        # Display timer
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self._update_display)
        self.display_timer.start(1000)

    def _connect_signals(self) -> None:
        self.start_btn.clicked.connect(self._start_jiggling)
        self.stop_btn.clicked.connect(self._stop_jiggling)

    def _start_jiggling(self) -> None:
        if self.is_running:
            return
        
        self.is_running = True
        self.jiggle_count = 0
        self.session_start = datetime.now()
        self.total_sessions += 1
        
        interval_ms = self.interval_spin.value() * 1000
        self.timer.start(interval_ms)
        
        self.status_icon.setText("🖱️")
        self.status_label.setText("Active")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #34d399;")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pattern_combo.setEnabled(False)
        self.interval_spin.setEnabled(False)
        
        self._do_jiggle()
        self._update_stats()

    def _stop_jiggling(self) -> None:
        if not self.is_running:
            return
        
        self.is_running = False
        self.timer.stop()
        
        if self.session_start:
            elapsed = (datetime.now() - self.session_start).seconds // 60
            self.total_minutes += elapsed
        
        self.status_icon.setText("💤")
        self.status_label.setText("Inactive")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pattern_combo.setEnabled(True)
        self.interval_spin.setEnabled(True)
        self.session_start = None
        self._update_stats()

    def _do_jiggle(self) -> None:
        if not self.is_running:
            return
        
        try:
            pattern = self.pattern_combo.currentText()
            caffeine = self.caffeine_check.isChecked()
            
            if "Invisible" in pattern or caffeine:
                pyautogui.moveRel(0, 0)
            elif "Subtle" in pattern:
                pyautogui.moveRel(1, 0, duration=0.05)
                pyautogui.moveRel(-1, 0, duration=0.05)
            elif "Circle" in pattern:
                import math
                cx, cy = pyautogui.position()
                for i in range(8):
                    a = (i / 8) * 2 * math.pi
                    pyautogui.moveRel(int(2*math.cos(a)), int(2*math.sin(a)), duration=0.02)
                pyautogui.moveTo(cx, cy, duration=0.05)
            elif "Random" in pattern:
                dx, dy = random.randint(-3, 3), random.randint(-3, 3)
                pyautogui.moveRel(dx, dy, duration=0.05)
                pyautogui.moveRel(-dx, -dy, duration=0.05)
            elif "Square" in pattern:
                for dx, dy in [(2, 0), (0, 2), (-2, 0), (0, -2)]:
                    pyautogui.moveRel(dx, dy, duration=0.03)
            
            self.jiggle_count += 1
            self.total_jiggles += 1
            self.jiggle_counter.setText(f"Jiggles: {self.jiggle_count}")
        except Exception:
            pass

    def _check_schedule(self) -> None:
        if not self.schedule_check.isChecked():
            return
        
        now = datetime.now()
        day_map = {"M": 0, "T": 1, "W": 2, "Th": 3, "F": 4}
        current_day = now.weekday()
        
        # Check if today is enabled
        day_enabled = False
        for day_name, cb in self.day_checks.items():
            if cb.isChecked() and day_map.get(day_name) == current_day:
                day_enabled = True
                break
        
        if not day_enabled:
            if self.is_running:
                self._stop_jiggling()
            return
        
        start = self.start_time.time()
        end = self.end_time.time()
        current = QTime.currentTime()
        
        in_window = start <= current <= end
        
        if in_window and not self.is_running:
            self._start_jiggling()
        elif not in_window and self.is_running:
            self._stop_jiggling()

    def _update_display(self) -> None:
        if self.session_start:
            elapsed = datetime.now() - self.session_start
            h, rem = divmod(int(elapsed.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            self.session_time.setText(f"Session: {h:02d}:{m:02d}:{s:02d}")

    def _update_stats(self) -> None:
        self.stats_sessions.setText(f"Sessions: {self.total_sessions}")
        self.stats_jiggles.setText(f"Total jiggles: {self.total_jiggles}")
        h, m = divmod(self.total_minutes, 60)
        self.stats_uptime.setText(f"Uptime: {h}h {m}m")

    def _reset_stats(self) -> None:
        self.total_sessions = 0
        self.total_jiggles = 0
        self.total_minutes = 0
        self._update_stats()

    def filter_items(self, text: str) -> None:
        pass

    def closeEvent(self, event) -> None:
        self._stop_jiggling()
        super().closeEvent(event)
