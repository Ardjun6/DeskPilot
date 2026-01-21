from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
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
from .views.flow_view import FlowView
from .views.launch_view import LaunchView
from .views.macro_view import MacroView
from .views.settings_view import SettingsView
from .views.template_view import TemplateView


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
        self.theme_combo.addItems(["dark", "light", "classic", "auto"])
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
        self.macro_view = MacroView(config_manager, macro_engine, log_callback=self._append_result)
        self.flow_view = FlowView(config_manager, action_engine, log_callback=self._append_result)
        self.launch_view = LaunchView(config_manager, action_engine, log_callback=self._append_result)
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
        self.stack.addWidget(self.flow_view)
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
        top_layout.addWidget(QLabel("Theme"))
        top_layout.addWidget(self.theme_combo)

        main_layout = QVBoxLayout()
        main_layout.addWidget(top_bar)
        main_layout.addWidget(self.stack, 1)
        main_layout.addWidget(self._build_log_panel())

        container = QWidget()
        container.setLayout(main_layout)

        root_layout = QHBoxLayout()
        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(container, 1)

        root_container = QWidget()
        root_container.setLayout(root_layout)
        self.setCentralWidget(root_container)

    def _connect_signals(self) -> None:
        self.sidebar.section_changed.connect(self._handle_section_changed)
        self.search_bar.textChanged.connect(self._handle_search)
        self.theme_combo.currentTextChanged.connect(self._handle_theme_change)
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
        from ..actions.results import RunResult  # lazy import to avoid cycle

        result = RunResult(status="success")
        result.add_log("INFO", f"Preview for {preview.name}")
        for line in preview.lines:
            result.add_log("DEBUG", line)
        self._append_result(result)

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
