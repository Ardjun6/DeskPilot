from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QApplication

from .config.config_manager import ConfigManager
from .actions.engine import ActionEngine
from .actions.macro_engine import MacroEngine
from .ui.main_window import MainWindow
from .ui.theme_manager import ThemeManager
from .utils.logging_utils import get_logger


class DeskPilotApp:
    """Application orchestrator that wires config, services, and UI."""

    def __init__(self, qt_app: QApplication, theme_manager: ThemeManager) -> None:
        self.qt_app = qt_app
        self.theme_manager = theme_manager
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager()
        self.action_engine: ActionEngine | None = None
        self.macro_engine: MacroEngine | None = None
        self.main_window: Optional[MainWindow] = None
        self._initialize()

    def _initialize(self) -> None:
        self.logger.debug("Initializing DeskPilot application")
        self.config_manager.ensure_loaded()
        self.action_engine = ActionEngine(config=self.config_manager)
        self.macro_engine = MacroEngine(config=self.config_manager)
        self.main_window = MainWindow(
            config_manager=self.config_manager,
            action_engine=self.action_engine,
            macro_engine=self.macro_engine,
            theme_manager=self.theme_manager,
        )

    def show(self) -> None:
        if self.main_window is not None:
            self.main_window.show()
