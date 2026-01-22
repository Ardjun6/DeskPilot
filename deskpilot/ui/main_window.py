from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..config.config_manager import ConfigManager
from ..actions.engine import ActionEngine
from .command_palette import CommandPalette
from .sidebar import Sidebar
from .theme_manager import THEMES, ThemeManager
from .executor import ExecutionWorker
from .views.action_view import ActionView
from .views.launch_view import LaunchView
from .views.macro_view import MacroView
from .views.settings_view import SettingsView
from .views.template_view import TemplateView
from .widgets.preview_dialog import PreviewDialog


class MainWindow(QMainWindow):
    """Primary application window with sidebar navigation and stacked views."""

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
        self.sidebar = Sidebar()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search actions or press Ctrl+K")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()) + ["auto"])
        self.theme_combo.setCurrentText(self.theme_manager.current_key)
        self.nav_combo = QComboBox()
        self.nav_combo.addItems(["Left", "Right", "Top", "Bottom"])
        self.nav_combo.setCurrentText("Left")
        self.command_button = QPushButton("⌘ Command Palette")
        self.command_button.setProperty("primary", True)
        self.stack = QStackedWidget()
        self.log_panel = QPlainTextEdit()
        self.log_panel.setObjectName("LogPanel")
        self.log_panel.setReadOnly(True)
        self.log_filter = QComboBox()
        self.log_filter.addItems(["ALL", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.log_copy = QPushButton("Copy logs")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)

        self.action_view = ActionView(config_manager, action_engine)
        self.template_view = TemplateView(config_manager, action_engine, log_callback=self._append_result)
        self.macro_view = MacroView(
            config_manager, macro_engine, log_callback=self._append_result, theme_manager=self.theme_manager
        )
        self.launch_view = LaunchView(
            config_manager, action_engine, log_callback=self._append_result, theme_manager=self.theme_manager
        )
        self.settings_view = SettingsView(config_manager)

        self.command_palette = CommandPalette(self, provider=self._provide_actions)
        self.shortcut_command = QShortcut(QKeySequence("Ctrl+K"), self)
        self.current_worker: ExecutionWorker | None = None
        self.recent_items: list[str] = []
        self.max_recent_items = 6

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.stack.addWidget(self.action_view)
        self.stack.addWidget(self.template_view)
        self.stack.addWidget(self.macro_view)
        self.stack.addWidget(self.launch_view)
        self.stack.addWidget(self.settings_view)

        top_bar = QWidget()
        top_bar.setObjectName("Toolbar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(8, 8, 8, 8)
        top_layout.setSpacing(10)
        top_layout.addWidget(QLabel("DeskPilot"))
        top_layout.addWidget(self.search_bar, 1)
        top_layout.addWidget(self.command_button)
        top_layout.addWidget(QLabel("Nav"))
        top_layout.addWidget(self.nav_combo)
        top_layout.addWidget(QLabel("Theme"))
        top_layout.addWidget(self.theme_combo)

        main_layout = QVBoxLayout()
        main_layout.addWidget(top_bar)
        main_layout.addWidget(self.stack, 1)
        main_layout.addWidget(self._build_log_panel())

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

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
        self.theme_combo.currentTextChanged.connect(self._handle_theme_change)
        self.nav_combo.currentTextChanged.connect(self._handle_nav_change)
        self.command_button.clicked.connect(self._open_command_palette)
        self.command_palette.action_chosen.connect(self._run_from_palette)
        self.shortcut_command.activated.connect(self._open_command_palette)
        self.log_copy.clicked.connect(self._copy_logs)
        self.stop_button.clicked.connect(self._stop_current)

    def _handle_section_changed(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

    def _handle_search(self, text: str) -> None:
        widget = self.stack.currentWidget()
        if hasattr(widget, "filter_items"):
            widget.filter_items(text)

    def _handle_theme_change(self, key: str) -> None:
        self.theme_manager.set_theme(key)

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
        self.sidebar.set_orientation(position.lower())

    def _build_log_panel(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 4, 0, 0)
        label = QLabel("Execution log")
        label.setObjectName("ActionDesc")
        header = QHBoxLayout()
        header.addWidget(label)
        header.addStretch()
        header.addWidget(self.log_filter)
        header.addWidget(self.stop_button)
        header.addWidget(self.log_copy)
        layout.addLayout(header)
        layout.addWidget(self.log_panel)
        return wrapper

    def _append_result(self, result) -> None:
        for log in result.logs:
            if self._log_visible(log.level):
                ts = log.timestamp.strftime("%H:%M:%S")
                self.log_panel.appendPlainText(f"{ts} [{log.level}] {log.message}")
        for err in result.errors:
            self.log_panel.appendPlainText(f"[ERROR] {err.message}")

    def _provide_actions(self, text: str):
        term = text.lower()
        items = []
        suggested_ids: set[str] = set()
        if not term:
            for item_id in self.recent_items:
                label = self._label_for_action_id(item_id)
                if label:
                    items.append((item_id, f"★ Suggested {label}"))
                    suggested_ids.add(item_id)
        for a in self.action_engine.list_actions():
            if term in a.name.lower() or term in a.description.lower():
                action_id = a.id
                if action_id not in suggested_ids:
                    items.append((action_id, f"[Action] {a.name} — {a.description}"))
        for m in self.macro_engine.list_macros():
            if term in m.name.lower() or term in m.description.lower():
                macro_id = f"macro:{m.id}"
                if macro_id not in suggested_ids:
                    items.append((macro_id, f"[Macro] {m.name} — {m.description}"))
        for name in self.config_manager.profiles.profiles.keys():
            if term in name.lower():
                profile_id = f"profile:{name}"
                if profile_id not in suggested_ids:
                    items.append((profile_id, f"[Profile] {name}"))
        return items

    def _open_command_palette(self) -> None:
        self.command_palette.open_centered()

    def _run_from_palette(self, action_id: str) -> None:
        self.search_bar.clear()
        self._record_recent(action_id)
        if action_id.startswith("macro:"):
            self.macro_view._run_macro(action_id.split(":", 1)[1])  # type: ignore[attr-defined]
        elif action_id.startswith("profile:"):
            self.launch_view._run_profile_name(action_id.split(":", 1)[1])  # type: ignore[attr-defined]
        else:
            self.run_action(action_id)

    def run_action(self, action_id: str) -> None:
        if self.current_worker:
            return
        self._record_recent(action_id)
        worker = ExecutionWorker(self.action_engine, action_id)
        self.current_worker = worker
        self.stop_button.setEnabled(True)
        worker.finished_with_result.connect(self._on_worker_finished)
        worker.start()

    def preview_action(self, action_id: str) -> None:
        preview = self.action_engine.preview(action_id)
        dialog = PreviewDialog(
            title=f"Preview: {preview.name}",
            summary=f"Action preview for {preview.name}.",
            steps=preview.lines,
            theme_manager=self.theme_manager,
            parent=self,
        )
        dialog.exec()

    def _on_worker_finished(self, result):
        self.current_worker = None
        self.stop_button.setEnabled(False)
        self._append_result(result)

    def _log_visible(self, level: str) -> bool:
        selected = self.log_filter.currentText()
        return selected == "ALL" or selected == level

    def _copy_logs(self) -> None:
        self.log_panel.selectAll()
        self.log_panel.copy()
        self.log_panel.moveCursor(self.log_panel.textCursor().End)

    def _stop_current(self) -> None:
        if self.current_worker:
            self.current_worker.request_cancel()

    def _record_recent(self, action_id: str) -> None:
        if action_id in self.recent_items:
            self.recent_items.remove(action_id)
        self.recent_items.insert(0, action_id)
        if len(self.recent_items) > self.max_recent_items:
            self.recent_items = self.recent_items[: self.max_recent_items]

    def _label_for_action_id(self, action_id: str) -> Optional[str]:
        if action_id.startswith("macro:"):
            macro = self.macro_engine.get_macro(action_id.split(":", 1)[1])
            if macro:
                return f"[Macro] {macro.name} — {macro.description}"
            return None
        if action_id.startswith("profile:"):
            name = action_id.split(":", 1)[1]
            return f"[Profile] {name}"
        action = self.action_engine.get_action(action_id)
        if action:
            return f"[Action] {action.name} — {action.description}"
        return None

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        message = (
            "Do you want me to become a ghost so timers keep running in the background?\n"
            "Yes = keep running, No = exit fully."
        )
        choice = QMessageBox.question(self, "Become a ghost?", message, QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.hide()
            event.ignore()
            return
        event.accept()
