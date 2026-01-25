"""Clipboard manager with history tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPoint
from PySide6.QtGui import QClipboard, QMouseEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QApplication,
    QLineEdit,
)


@dataclass
class ClipboardEntry:
    """A single clipboard history entry."""
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    pinned: bool = False
    
    @property
    def preview(self) -> str:
        """Get preview text (first 50 chars)."""
        text = self.content.replace('\n', ' ').strip()
        if len(text) > 50:
            return text[:47] + "..."
        return text
    
    @property
    def time_ago(self) -> str:
        """Get human-readable time ago."""
        delta = datetime.now() - self.timestamp
        if delta.seconds < 60:
            return "just now"
        elif delta.seconds < 3600:
            return f"{delta.seconds // 60}m ago"
        elif delta.seconds < 86400:
            return f"{delta.seconds // 3600}h ago"
        else:
            return f"{delta.days}d ago"


class ClipboardEntryWidget(QFrame):
    """Widget displaying a single clipboard entry."""

    paste_requested = Signal(str)
    pin_toggled = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, entry: ClipboardEntry, index: int, colors: dict, parent=None) -> None:
        super().__init__(parent)
        self.entry = entry
        self.index = index
        self.colors = colors
        self._build_ui()

    def _build_ui(self) -> None:
        self.setProperty("card", True)
        self.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['surface']};
                border: 1px solid {self.colors['border_soft']};
                border-radius: 6px;
                padding: 4px;
            }}
            QFrame:hover {{
                border-color: {self.colors['accent']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Content preview
        preview = QLabel(self.entry.preview)
        preview.setWordWrap(True)
        preview.setStyleSheet("font-size: 12px;")
        layout.addWidget(preview)
        
        # Bottom row with time and actions
        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        
        time_label = QLabel(self.entry.time_ago)
        time_label.setStyleSheet(f"font-size: 10px; color: {self.colors['text_muted']};")
        bottom.addWidget(time_label)
        
        if self.entry.pinned:
            pin_label = QLabel("📌")
            bottom.addWidget(pin_label)
        
        bottom.addStretch()
        
        # Paste button
        paste_btn = QPushButton("Paste")
        paste_btn.setFixedHeight(22)
        paste_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
            }}
        """)
        paste_btn.clicked.connect(lambda: self.paste_requested.emit(self.entry.content))
        bottom.addWidget(paste_btn)
        
        # Pin button
        pin_btn = QPushButton("📌" if not self.entry.pinned else "📍")
        pin_btn.setFixedSize(22, 22)
        pin_btn.setToolTip("Pin" if not self.entry.pinned else "Unpin")
        pin_btn.clicked.connect(lambda: self.pin_toggled.emit(self.index))
        bottom.addWidget(pin_btn)
        
        # Delete button
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(22, 22)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        bottom.addWidget(del_btn)
        
        layout.addLayout(bottom)


class ClipboardPopup(QWidget):
    """Popup window showing clipboard history."""

    def __init__(self, manager: "ClipboardManager", colors: dict, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.colors = colors
        self._drag_position: Optional[QPoint] = None
        
        self._setup_window()
        self._build_ui()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setFixedSize(320, 400)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg']};
                color: {self.colors['text']};
            }}
            QLineEdit {{
                background: {self.colors['surface']};
                border: 1px solid {self.colors['border_soft']};
                border-radius: 6px;
                padding: 8px;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        
        title = QLabel("📋 Clipboard History")
        title.setStyleSheet("font-size: 14px; font-weight: 600;")
        header.addWidget(title)
        
        header.addStretch()
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        header.addWidget(clear_btn)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)
        
        layout.addLayout(header)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search clipboard...")
        self.search.textChanged.connect(self._refresh_list)
        layout.addWidget(self.search)

        # History list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(6)
        
        scroll.setWidget(self.list_container)
        layout.addWidget(scroll)

    def _refresh_list(self) -> None:
        """Refresh the clipboard entries list."""
        # Clear existing
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        search_text = self.search.text().lower()
        
        # Add entries (pinned first)
        entries = self.manager.history
        sorted_entries = sorted(entries, key=lambda e: (not e.pinned, e.timestamp), reverse=True)
        
        for i, entry in enumerate(sorted_entries):
            if search_text and search_text not in entry.content.lower():
                continue
            
            widget = ClipboardEntryWidget(entry, i, self.colors)
            widget.paste_requested.connect(self._paste_entry)
            widget.pin_toggled.connect(self._toggle_pin)
            widget.delete_requested.connect(self._delete_entry)
            self.list_layout.addWidget(widget)
        
        self.list_layout.addStretch()
        
        if not entries:
            empty = QLabel("No clipboard history yet")
            empty.setStyleSheet(f"color: {self.colors['text_muted']}; padding: 20px;")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty)

    def _paste_entry(self, content: str) -> None:
        """Paste the selected entry."""
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        self.hide()

    def _toggle_pin(self, index: int) -> None:
        """Toggle pin status."""
        if 0 <= index < len(self.manager.history):
            self.manager.history[index].pinned = not self.manager.history[index].pinned
            self._refresh_list()

    def _delete_entry(self, index: int) -> None:
        """Delete an entry."""
        if 0 <= index < len(self.manager.history):
            self.manager.history.pop(index)
            self._refresh_list()

    def _clear_all(self) -> None:
        """Clear all non-pinned entries."""
        self.manager.history = [e for e in self.manager.history if e.pinned]
        self._refresh_list()

    def showEvent(self, event) -> None:
        """Refresh when shown."""
        self._refresh_list()
        super().showEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPosition().toPoint() - self._drag_position)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_position = None


class ClipboardManager(QObject):
    """Manages clipboard history and monitoring."""

    entry_added = Signal(ClipboardEntry)

    def __init__(self, colors: dict, max_history: int = 50, parent=None) -> None:
        super().__init__(parent)
        self.colors = colors
        self.max_history = max_history
        self.history: List[ClipboardEntry] = []
        self._last_content: str = ""
        self.popup: Optional[ClipboardPopup] = None
        
        # Start monitoring clipboard
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self._on_clipboard_change)
        
        # Also poll periodically (some systems don't emit dataChanged)
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_clipboard)
        self.poll_timer.start(1000)  # Check every second

    def _on_clipboard_change(self) -> None:
        """Handle clipboard content change."""
        self._check_and_add()

    def _poll_clipboard(self) -> None:
        """Poll clipboard for changes."""
        self._check_and_add()

    def _check_and_add(self) -> None:
        """Check if clipboard has new content and add to history."""
        text = self.clipboard.text()
        if text and text != self._last_content:
            self._last_content = text
            self.add_entry(text)

    def add_entry(self, content: str) -> None:
        """Add a new entry to history."""
        # Don't add duplicates of most recent
        if self.history and self.history[0].content == content:
            return
        
        entry = ClipboardEntry(content=content)
        self.history.insert(0, entry)
        
        # Trim history (keep pinned)
        if len(self.history) > self.max_history:
            # Keep pinned entries
            pinned = [e for e in self.history if e.pinned]
            unpinned = [e for e in self.history if not e.pinned]
            self.history = pinned + unpinned[:self.max_history - len(pinned)]
        
        self.entry_added.emit(entry)

    def show_popup(self) -> None:
        """Show the clipboard history popup."""
        if self.popup is None:
            self.popup = ClipboardPopup(self, self.colors)
        
        # Position near cursor
        from PySide6.QtGui import QCursor
        cursor_pos = QCursor.pos()
        self.popup.move(cursor_pos.x() - 160, cursor_pos.y() + 20)
        self.popup.show()
        self.popup.raise_()

    def get_recent(self, count: int = 10) -> List[ClipboardEntry]:
        """Get recent entries."""
        return self.history[:count]
