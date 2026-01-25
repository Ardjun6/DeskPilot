"""Coordinate Picker - Fullscreen overlay to pick screen coordinates."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QPoint, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QCursor
from PySide6.QtWidgets import QWidget, QApplication, QLabel


class CoordinatePicker(QWidget):
    """Fullscreen overlay to pick coordinates with live preview."""
    
    coordinate_picked = Signal(int, int)  # x, y
    cancelled = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        
        # Cover all screens
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.virtualGeometry()
            self.setGeometry(geo)
        
        self.current_pos = QPoint(0, 0)
        
        # Update timer for smooth coordinate display
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_position)
        self.update_timer.start(16)  # ~60fps
    
    def _update_position(self) -> None:
        self.current_pos = QCursor.pos()
        self.update()
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        
        # Crosshair at cursor
        x, y = self.current_pos.x(), self.current_pos.y()
        
        # Draw crosshair lines
        painter.setPen(QColor(59, 130, 246, 180))
        painter.drawLine(x, 0, x, self.height())
        painter.drawLine(0, y, self.width(), y)
        
        # Draw coordinate label near cursor
        label_text = f"X: {x}  Y: {y}"
        
        # Label background
        font = QFont("Segoe UI", 11, QFont.Bold)
        painter.setFont(font)
        
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(label_text) + 20
        text_height = fm.height() + 10
        
        # Position label above and to the right of cursor
        label_x = x + 20
        label_y = y - 30
        
        # Keep on screen
        if label_x + text_width > self.width():
            label_x = x - text_width - 10
        if label_y < 10:
            label_y = y + 30
        
        # Draw label background
        painter.setBrush(QColor(59, 130, 246))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(label_x, label_y, text_width, text_height, 6, 6)
        
        # Draw label text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(label_x + 10, label_y + fm.ascent() + 5, label_text)
        
        # Instructions at bottom
        instruction = "Click to select • ESC to cancel"
        inst_width = fm.horizontalAdvance(instruction) + 40
        inst_x = (self.width() - inst_width) // 2
        inst_y = self.height() - 60
        
        painter.setBrush(QColor(30, 30, 30, 200))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(inst_x, inst_y, inst_width, 40, 8, 8)
        
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(inst_x + 20, inst_y + fm.ascent() + 12, instruction)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            pos = QCursor.pos()
            self.coordinate_picked.emit(pos.x(), pos.y())
            self.close()
    
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.cancelled.emit()
            self.close()
    
    def showEvent(self, event) -> None:
        self.activateWindow()
        self.raise_()
        super().showEvent(event)


def pick_coordinates(callback) -> CoordinatePicker:
    """
    Show coordinate picker and call callback with (x, y) when picked.
    
    Usage:
        def on_picked(x, y):
            print(f"Picked: {x}, {y}")
        
        picker = pick_coordinates(on_picked)
        picker.show()
    """
    picker = CoordinatePicker()
    picker.coordinate_picked.connect(callback)
    picker.show()
    return picker
