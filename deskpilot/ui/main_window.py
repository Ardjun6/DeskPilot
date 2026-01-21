from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from ..config.config_manager import ConfigManager
from .sidebar import Sidebar
from .views.flow_view import FlowView
from .views.launch_view import LaunchView
from .views.macro_view import MacroView
from .views.settings_view import SettingsView
from .views.template_view import TemplateView


class MainWindow(QMainWindow):
    """Primary application window with sidebar navigation and stacked views."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("DeskPilot")
        self.sidebar = Sidebar()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search current view...")
        self.stack = QStackedWidget()

        self.template_view = TemplateView(config_manager)
        self.macro_view = MacroView(config_manager)
        self.flow_view = FlowView(config_manager)
        self.launch_view = LaunchView(config_manager)
        self.settings_view = SettingsView(config_manager)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.stack.addWidget(self.template_view)
        self.stack.addWidget(self.macro_view)
        self.stack.addWidget(self.flow_view)
        self.stack.addWidget(self.launch_view)
        self.stack.addWidget(self.settings_view)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(self.stack)

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

    def _handle_section_changed(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

    def _handle_search(self, text: str) -> None:
        widget = self.stack.currentWidget()
        if hasattr(widget, "filter_items"):
            widget.filter_items(text)
