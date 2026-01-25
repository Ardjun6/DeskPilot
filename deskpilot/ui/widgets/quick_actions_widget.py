"""Floating quick actions widget - minimizable, always on top."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
)

if TYPE_CHECKING:
    from ..actions.engine import ActionEngine


class QuickActionsWidget(QWidget):
    """Floating widget with minimize/expand functionality."""

    action_triggered = Signal(str)

    def __init__(
        self,
        action_engine: "ActionEngine",
        colors: dict,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.action_engine = action_engine
        self.colors = colors
        self._drag_position: Optional[QPoint] = None
        self._is_minimized = False
        
        self._setup_window()
        self._build_ui()
        self.refresh_actions()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self._expanded_width = 220
        self._expanded_height = 300
        self._minimized_width = 50
        self._minimized_height = 50
        self.setFixedSize(self._expanded_width, self._expanded_height)
        
        self.setStyleSheet(f"""
            QWidget#QuickWidget {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: {self.colors['bg_alt']};
                border: 1px solid {self.colors['border_soft']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                text-align: left;
                color: {self.colors['text']};
            }}
            QPushButton:hover {{
                background-color: {self.colors['accent']};
                color: white;
                border-color: {self.colors['accent']};
            }}
            QLabel {{
                color: {self.colors['text']};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """)

    def _build_ui(self) -> None:
        self.main_widget = QWidget()
        self.main_widget.setObjectName("QuickWidget")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_widget)
        
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        header.setSpacing(8)
        
        self.title = QLabel("⚡ Quick Actions")
        self.title.setStyleSheet("font-size: 13px; font-weight: 600;")
        header.addWidget(self.title)
        
        header.addStretch()
        
        # Minimize button
        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(24, 24)
        self.min_btn.setToolTip("Minimize")
        self.min_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['bg_alt']};
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self.colors['accent']};
            }}
        """)
        self.min_btn.clicked.connect(self._toggle_minimize)
        header.addWidget(self.min_btn)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['bg_alt']};
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: #ef4444;
                color: white;
            }}
        """)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)
        
        layout.addLayout(header)

        # Content container
        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")
        
        self.buttons_container = QWidget()
        self.buttons_container.setStyleSheet("background: transparent;")
        self.buttons_layout = QVBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(4)
        
        scroll.setWidget(self.buttons_container)
        content_layout.addWidget(scroll, 1)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_actions)
        content_layout.addWidget(refresh_btn)
        
        layout.addWidget(self.content)
        
        # Minimized view
        self.minimized_widget = QWidget()
        self.minimized_widget.setObjectName("QuickWidget")
        min_layout = QVBoxLayout(self.minimized_widget)
        min_layout.setContentsMargins(0, 0, 0, 0)
        
        expand_btn = QPushButton("⚡")
        expand_btn.setFixedSize(46, 46)
        expand_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['accent']};
                border: none;
                border-radius: 12px;
                font-size: 20px;
                color: white;
            }}
            QPushButton:hover {{
                background: {self.colors.get('accent_dark', self.colors['accent'])};
            }}
        """)
        expand_btn.setToolTip("Expand Quick Actions")
        expand_btn.clicked.connect(self._toggle_minimize)
        min_layout.addWidget(expand_btn)
        
        main_layout.addWidget(self.minimized_widget)
        self.minimized_widget.hide()

    def _toggle_minimize(self) -> None:
        if self._is_minimized:
            self._is_minimized = False
            self.minimized_widget.hide()
            self.main_widget.show()
            self.setFixedSize(self._expanded_width, self._expanded_height)
        else:
            self._is_minimized = True
            self.main_widget.hide()
            self.minimized_widget.show()
            self.setFixedSize(self._minimized_width, self._minimized_height)

    def refresh_actions(self) -> None:
        while self.buttons_layout.count():
            item = self.buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        actions = self.action_engine.list_actions()
        favorites = [a for a in actions if a.favorite]
        display_actions = favorites if favorites else actions[:8]
        
        for action in display_actions[:10]:
            btn = QPushButton(f"▶  {action.name}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, aid=action.id: self._on_action_clicked(aid)
            )
            self.buttons_layout.addWidget(btn)
        
        if not display_actions:
            empty = QLabel("No actions yet")
            empty.setStyleSheet(f"color: {self.colors['text_muted']}; padding: 20px;")
            empty.setAlignment(Qt.AlignCenter)
            self.buttons_layout.addWidget(empty)
        
        self.buttons_layout.addStretch()

    def _on_action_clicked(self, action_id: str) -> None:
        self.action_triggered.emit(action_id)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_position = None

    def show_at_cursor(self) -> None:
        from PySide6.QtGui import QCursor
        cursor_pos = QCursor.pos()
        self.move(cursor_pos.x() - 110, cursor_pos.y() + 20)
        self.show()
        self.raise_()
