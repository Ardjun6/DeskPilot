"""Splash screen for DeskPilot startup with animated progress."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsOpacityEffect, QProgressBar


class SplashScreen(QWidget):
    """Clean animated splash screen with progress bar."""

    def __init__(self, colors: dict, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.colors = colors
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setFixedSize(400, 280)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['bg']};
                color: {colors['text']};
            }}
            QLabel {{
                background: transparent;
            }}
            QProgressBar {{
                background: {colors['border_soft']};
                border: none;
                border-radius: 4px;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background: {colors['accent']};
                border-radius: 4px;
            }}
        """)

        self._build_ui()
        self._center_on_screen()
        self._start_animation()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 40)
        layout.setSpacing(16)

        # Logo emoji
        logo = QLabel("✈")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"font-size: 64px;")
        layout.addWidget(logo)

        # Title
        title = QLabel("DeskPilot")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {self.colors['text']}; letter-spacing: 2px;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Desktop Automation")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 12px; color: {self.colors['text_muted']}; letter-spacing: 1px;")
        layout.addWidget(subtitle)

        layout.addStretch()

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        layout.addWidget(self.progress)

        # Status text
        self.status = QLabel("Loading...")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet(f"font-size: 11px; color: {self.colors['text_muted']};")
        layout.addWidget(self.status)

    def _center_on_screen(self) -> None:
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.center().x() - self.width() // 2, geo.center().y() - self.height() // 2)

    def _start_animation(self) -> None:
        self.progress_value = 0
        self.status_messages = [
            (0, "Loading configuration..."),
            (25, "Initializing actions..."),
            (50, "Setting up hotkeys..."),
            (75, "Preparing interface..."),
            (95, "Almost ready..."),
        ]
        self._animate_progress()

    def _animate_progress(self) -> None:
        if self.progress_value <= 100:
            self.progress.setValue(self.progress_value)
            
            # Update status message
            for threshold, message in self.status_messages:
                if self.progress_value >= threshold:
                    self.status.setText(message)
            
            self.progress_value += 2
            QTimer.singleShot(20, self._animate_progress)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(self.colors['bg']))
        painter.setPen(QColor(self.colors['border']))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 16, 16)


class SplashManager:
    """Manages splash screen lifecycle."""

    def __init__(self, colors: dict) -> None:
        self.splash: Optional[SplashScreen] = None
        self.colors = colors

    def show(self) -> None:
        self.splash = SplashScreen(self.colors)
        self.splash.show()

    def finish(self, main_window: QWidget, fade_duration: int = 300) -> None:
        if self.splash is None:
            main_window.show()
            return

        opacity = QGraphicsOpacityEffect(self.splash)
        self.splash.setGraphicsEffect(opacity)

        anim = QPropertyAnimation(opacity, b"opacity")
        anim.setDuration(fade_duration)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        def on_finished():
            if self.splash:
                self.splash.close()
                self.splash = None
            main_window.show()

        anim.finished.connect(on_finished)
        anim.start()
        self.splash._fade_anim = anim

    def close(self) -> None:
        if self.splash:
            self.splash.close()
            self.splash = None
