from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QApplication

from .config.config_manager import ConfigManager
from .ui.main_window import MainWindow
from .utils.logging_utils import get_logger


class DeskPilotApp:
    """Application orchestrator that wires config, services, and UI."""

    def __init__(self, qt_app: QApplication) -> None:
        self.qt_app = qt_app
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager()
        self.main_window: Optional[MainWindow] = None
        self._initialize()

    def _initialize(self) -> None:
        self.logger.debug("Initializing DeskPilot application")
        self.config_manager.ensure_loaded()
        self.main_window = MainWindow(config_manager=self.config_manager)

    def show(self) -> None:
        if self.main_window is not None:
            self.main_window.show()
