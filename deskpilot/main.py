from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication

from .app import DeskPilotApp
from .build import build_exe
from .ui.theme_manager import ThemeManager


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DeskPilot launcher")
    parser.add_argument(
        "--build-exe",
        action="store_true",
        help="Build a Windows executable using PyInstaller.",
    )
    args = parser.parse_args(argv)

    if args.build_exe:
        return build_exe()

    app = QApplication(sys.argv)
    theme_manager = ThemeManager(app, default="dark")
    deskpilot = DeskPilotApp(app, theme_manager=theme_manager)
    deskpilot.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
