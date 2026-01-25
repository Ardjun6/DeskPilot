"""Main window with system tray, quick widget, clipboard, and all views."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QKeySequence, QShortcut, QCloseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from ..config.config_manager import ConfigManager
from ..actions.engine import ActionEngine
from .command_palette import CommandPalette
from .sidebar import Sidebar
from .theme_manager import THEMES, ThemeManager
from .executor import ExecutionWorker
from .system_tray import SystemTrayManager
from .views.action_view import ActionView
from .views.template_view import TemplateView
from .views.workflow_builder_view import WorkflowBuilderView
from .views.recorder_view import RecorderView
from .views.launcher_editor_view import LauncherEditorView
from .views.settings_view import SettingsView
from .widgets.preview_dialog import PreviewDialog
from .widgets.quick_actions_widget import QuickActionsWidget
from .widgets.clipboard_manager import ClipboardManager
from ..utils.hotkeys import HotkeyManager, HotkeyRegistrationError


class ClipboardView(QWidget):
    """Wrapper view for clipboard manager."""
    
    def __init__(self, clipboard_manager: ClipboardManager, parent=None) -> None:
        super().__init__(parent)
        self.clipboard_manager = clipboard_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("📋 Clipboard History")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch()
        
        popup_btn = QPushButton("📌 Open Popup")
        popup_btn.clicked.connect(clipboard_manager.show_popup)
        header.addWidget(popup_btn)
        layout.addLayout(header)
        
        # Info
        info = QLabel(
            "Your clipboard history is tracked automatically.\n\n"
            "• Click 'Open Popup' or use Ctrl+Shift+V for quick access\n"
            "• Pin important items to keep them\n"
            "• Search through your history\n"
            "• Clipboard is monitored in the background"
        )
        info.setObjectName("ActionDesc")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
    
    def filter_items(self, text: str) -> None:
        pass


class MainWindow(QMainWindow):
    """Main application window with all features."""

    def __init__(
        self,
        config_manager: ConfigManager,
        action_engine: ActionEngine,
        macro_engine,
        theme_manager: ThemeManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.action_engine = action_engine
        self.macro_engine = macro_engine
        self.theme_manager = theme_manager
        self.setWindowTitle("DeskPilot")
        self.setMinimumSize(900, 600)
        
        # UI Components
        self.sidebar = Sidebar()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or press Ctrl+K")
        
        self.theme_combo = QComboBox()
        for key, name in theme_manager.get_theme_display_names():
            self.theme_combo.addItem(name, key)
        self._set_theme_combo_by_key(self.theme_manager.current_key)
        
        self.nav_combo = QComboBox()
        self.nav_combo.addItems(["Left", "Right", "Top", "Bottom"])
        
        self.command_button = QPushButton("⌘ Commands")
        self.command_button.setProperty("primary", True)
        
        self.stack = QStackedWidget()
        
        # Log panel
        self.log_panel = QPlainTextEdit()
        self.log_panel.setObjectName("LogPanel")
        self.log_panel.setReadOnly(True)
        self.log_filter = QComboBox()
        self.log_filter.addItems(["ALL", "INFO", "WARNING", "ERROR"])
        self.log_copy = QPushButton("Copy")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        
        self.timer_label = QLabel("Timer: Idle")
        self.timer_label.setObjectName("ActionDesc")

        # Managers
        colors = theme_manager.current.colors
        self.clipboard_manager = ClipboardManager(colors)
        self.system_tray = SystemTrayManager()
        self.quick_widget = QuickActionsWidget(action_engine, colors)
        self.quick_widget.action_triggered.connect(self._run_action)
        self.quick_widget.hide()

        # Views
        self.action_view = ActionView(config_manager, action_engine)
        self.template_view = TemplateView(config_manager, action_engine, log_callback=self._append_result)
        self.workflow_view = WorkflowBuilderView(config_manager, theme_manager)
        self.recorder_view = RecorderView(config_manager, theme_manager)
        self.clipboard_view = ClipboardView(self.clipboard_manager)
        self.launcher_editor_view = LauncherEditorView(config_manager, theme_manager)
        self.settings_view = SettingsView(config_manager)

        self.command_palette = CommandPalette(self, provider=self._provide_actions)
        self.shortcut_command = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_clipboard = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.shortcut_quick = QShortcut(QKeySequence("Ctrl+Shift+Q"), self)
        
        self.current_worker: ExecutionWorker | None = None
        self.recent_items: list[str] = []
        self.max_recent_items = 6
        self.hotkey_manager = HotkeyManager()
        self._minimize_to_tray = True

        self._build_ui()
        self._connect_signals()
        self.refresh_hotkeys()
        
        # Setup system tray
        self.system_tray.setup(self)

    def _build_ui(self) -> None:
        # Add views to stack (order matches sidebar)
        self.stack.addWidget(self.action_view)        # 0
        self.stack.addWidget(self.template_view)      # 1
        self.stack.addWidget(self.workflow_view)      # 2
        self.stack.addWidget(self.recorder_view)      # 3
        self.stack.addWidget(self.clipboard_view)     # 4
        self.stack.addWidget(self.launcher_editor_view)  # 5
        self.stack.addWidget(self.settings_view)      # 6

        # Toolbar
        top_bar = QWidget()
        top_bar.setObjectName("Toolbar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 8, 12, 8)
        top_layout.setSpacing(10)
        
        brand = QLabel("✈ DeskPilot")
        brand.setStyleSheet("font-size: 15px; font-weight: 600;")
        top_layout.addWidget(brand)
        
        top_layout.addWidget(self.search_bar, 1)
        top_layout.addWidget(self.command_button)
        
        quick_btn = QPushButton("📌")
        quick_btn.setToolTip("Quick Actions Widget (Ctrl+Shift+Q)")
        quick_btn.clicked.connect(self._show_quick_widget)
        top_layout.addWidget(quick_btn)
        
        clip_btn = QPushButton("📋")
        clip_btn.setToolTip("Clipboard (Ctrl+Shift+V)")
        clip_btn.clicked.connect(self.clipboard_manager.show_popup)
        top_layout.addWidget(clip_btn)
        
        top_layout.addWidget(QLabel("Nav:"))
        top_layout.addWidget(self.nav_combo)
        top_layout.addWidget(QLabel("Theme:"))
        top_layout.addWidget(self.theme_combo)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)
        main_layout.addWidget(top_bar)
        main_layout.addWidget(self.stack, 1)
        main_layout.addWidget(self._build_log_panel())

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Nav dock
        self.nav_dock = QDockWidget("Navigation", self)
        self.nav_dock.setObjectName("NavDock")
        self.nav_dock.setTitleBarWidget(QWidget())
        self.nav_dock.setWidget(self.sidebar)
        self.nav_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.nav_dock.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea
        )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nav_dock)
        self.sidebar.set_orientation("left")

    def _connect_signals(self) -> None:
        self.sidebar.section_changed.connect(self._handle_section_changed)
        self.search_bar.textChanged.connect(self._handle_search)
        self.theme_combo.currentIndexChanged.connect(self._handle_theme_change)
        self.nav_combo.currentTextChanged.connect(self._handle_nav_change)
        self.command_button.clicked.connect(self._open_command_palette)
        self.command_palette.action_chosen.connect(self._run_from_palette)
        self.shortcut_command.activated.connect(self._open_command_palette)
        self.shortcut_clipboard.activated.connect(self.clipboard_manager.show_popup)
        self.shortcut_quick.activated.connect(self._show_quick_widget)
        self.log_copy.clicked.connect(self._copy_logs)
        self.stop_button.clicked.connect(self._stop_current)
        self.action_view.run_requested.connect(self._run_action)
        self.action_view.preview_requested.connect(self._preview_action)

    def _show_quick_widget(self) -> None:
        self.quick_widget.refresh_actions()
        self.quick_widget.show_at_cursor()

    def _handle_section_changed(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

    def _handle_search(self, text: str) -> None:
        widget = self.stack.currentWidget()
        if hasattr(widget, "filter_items"):
            widget.filter_items(text)

    def _handle_theme_change(self, index: int) -> None:
        key = self.theme_combo.itemData(index)
        if key:
            self.theme_manager.set_theme(key)

    def _set_theme_combo_by_key(self, key: str) -> None:
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == key:
                self.theme_combo.setCurrentIndex(i)
                return

    def _handle_nav_change(self, position: str) -> None:
        areas = {
            "Left": Qt.LeftDockWidgetArea,
            "Right": Qt.RightDockWidgetArea,
            "Top": Qt.TopDockWidgetArea,
            "Bottom": Qt.BottomDockWidgetArea,
        }
        area = areas.get(position, Qt.LeftDockWidgetArea)
        self.removeDockWidget(self.nav_dock)
        self.addDockWidget(area, self.nav_dock)
        self.nav_dock.show()
        self.sidebar.set_orientation(position.lower())

    def refresh_hotkeys(self) -> None:
        self.hotkey_manager.clear()
        
        for action in self.config_manager.actions.actions:
            if action.hotkey and action.enabled:
                try:
                    action_id = action.id
                    # Create a proper callback that's thread-safe
                    def make_callback(aid):
                        def callback():
                            # Use invokeMethod for thread safety
                            from PySide6.QtCore import QMetaObject, Qt as QtCore_Qt, Q_ARG
                            QMetaObject.invokeMethod(
                                self, "_run_action_safe",
                                QtCore_Qt.QueuedConnection,
                                Q_ARG(str, aid)
                            )
                        return callback
                    
                    self.hotkey_manager.register(action.hotkey, make_callback(action_id))
                except HotkeyRegistrationError as e:
                    print(f"Failed to register hotkey {action.hotkey}: {e}")
        
        # Refresh tray menu
        self.system_tray.refresh_actions()
    
    @Slot(str)
    def _run_action_safe(self, action_id: str) -> None:
        """Thread-safe action runner called from hotkey."""
        self._run_action(action_id)

    def _queue_ui(self, callback) -> None:
        QTimer.singleShot(0, callback)

    def _build_log_panel(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)
        
        header = QHBoxLayout()
        header.setSpacing(8)
        
        header.addWidget(QLabel("📋 Log"))
        header.addWidget(self.timer_label)
        header.addStretch()
        header.addWidget(self.log_filter)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.log_panel.clear)
        header.addWidget(clear_btn)
        header.addWidget(self.stop_button)
        header.addWidget(self.log_copy)
        
        layout.addLayout(header)
        self.log_panel.setMaximumHeight(100)
        layout.addWidget(self.log_panel)
        return wrapper

    def _append_result(self, result) -> None:
        for log in result.logs:
            if self._log_visible(log.level):
                ts = log.timestamp.strftime("%H:%M:%S")
                self.log_panel.appendPlainText(f"{ts} [{log.level}] {log.message}")
        for err in result.errors:
            self.log_panel.appendPlainText(f"[ERROR] {err.message}")

    def _log_visible(self, level: str) -> bool:
        f = self.log_filter.currentText()
        if f == "ALL":
            return True
        order = ["DEBUG", "INFO", "WARNING", "ERROR"]
        return level in order and f in order and order.index(level) >= order.index(f)

    def _copy_logs(self) -> None:
        text = self.log_panel.toPlainText()
        if text:
            QApplication.clipboard().setText(text)

    def _stop_current(self) -> None:
        if self.current_worker:
            self.current_worker.request_cancel()

    def _open_command_palette(self) -> None:
        self.command_palette.open_centered()

    def _provide_actions(self, query: str) -> list[tuple[str, str]]:
        query = query.lower()
        results = []
        for aid in self.recent_items:
            action = self.action_engine.get_action(aid)
            if action and query in action.name.lower():
                results.append((aid, f"⏱ {action.name}"))
        for action in self.config_manager.actions.actions:
            if action.id not in self.recent_items and query in action.name.lower():
                results.append((action.id, action.name))
        return results[:20]

    def _run_from_palette(self, action_id: str) -> None:
        self._update_recent(action_id)
        self._run_action(action_id)

    def _update_recent(self, action_id: str) -> None:
        if action_id in self.recent_items:
            self.recent_items.remove(action_id)
        self.recent_items.insert(0, action_id)
        if len(self.recent_items) > self.max_recent_items:
            self.recent_items.pop()

    def _run_action(self, action_id: str) -> None:
        if self.current_worker:
            return
        action = self.action_engine.get_action(action_id)
        if not action or not action.enabled:
            return
        
        self._update_recent(action_id)
        self.timer_label.setText(f"Running: {action.name}...")
        
        worker = ExecutionWorker(self.action_engine, action_id, inputs={})
        self.current_worker = worker
        self.stop_button.setEnabled(True)
        worker.finished_with_result.connect(self._on_action_finished)
        worker.start()

    def _on_action_finished(self, result) -> None:
        self.current_worker = None
        self.stop_button.setEnabled(False)
        self.timer_label.setText("Timer: Idle")
        self._append_result(result)

    def _preview_action(self, action_id: str) -> None:
        action = self.action_engine.get_action(action_id)
        if not action:
            return
        try:
            preview = self.action_engine.preview(action_id)
            lines = preview.lines
        except Exception as e:
            lines = [f"Error: {e}"]
        dialog = PreviewDialog(
            title=action.name,
            summary=action.description or "",
            steps=lines,
            theme_manager=self.theme_manager,
            parent=self,
        )
        dialog.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._minimize_to_tray:
            event.ignore()
            self.hide()
            self.system_tray.show_notification(
                "DeskPilot",
                "Running in background. Click tray icon to show."
            )
        else:
            self._cleanup_and_quit()
            event.accept()

    def _cleanup_and_quit(self) -> None:
        self.hotkey_manager.clear()
        if hasattr(self, 'jiggle_view'):
            self.jiggle_view._stop_jiggling()
        if hasattr(self, 'recorder_view') and self.recorder_view.recorder_thread:
            self.recorder_view.recorder_thread.stop()
        self.system_tray.hide()
