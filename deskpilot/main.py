from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

from .app import DeskPilotApp
from .ui.theme_manager import ThemeManager


def main() -> int:
    app = QApplication(sys.argv)
    theme_manager = ThemeManager(app, default="dark")
    deskpilot = DeskPilotApp(app, theme_manager=theme_manager)
    deskpilot.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
