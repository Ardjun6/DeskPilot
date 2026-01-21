from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

from .app import DeskPilotApp


def main() -> int:
    app = QApplication(sys.argv)
    deskpilot = DeskPilotApp(app)
    deskpilot.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
