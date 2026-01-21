from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .app import DeskPilotApp
from .ui.theme_manager import ThemeManager


def build_exe(required: bool = True) -> int:
    """Build a Windows executable using PyInstaller."""
    if importlib.util.find_spec("PyInstaller") is None:
        print("PyInstaller is required. Install with: pip install pyinstaller")
        return 1 if required else 0

    project_root = Path(__file__).resolve().parents[1]
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    script_path = project_root / "deskpilot" / "main.py"

    pyinstaller = importlib.import_module("PyInstaller.__main__")
    pyinstaller.run(
        [
            "--noconfirm",
            "--clean",
            "--windowed",
            "--onefile",
            "--name",
            "DeskPilot",
            "--distpath",
            str(dist_dir),
            "--workpath",
            str(build_dir),
            "--specpath",
            str(build_dir),
            str(script_path),
        ]
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DeskPilot launcher")
    parser.add_argument(
        "--build-exe",
        action="store_true",
        help="Build a Windows executable using PyInstaller.",
    )
    parser.add_argument(
        "--no-build-exe",
        action="store_true",
        help="Skip the automatic executable build step.",
    )
    args = parser.parse_args(argv)

    if args.build_exe:
        return build_exe(required=True)

    if not args.no_build_exe:
        build_exe(required=False)

    app = QApplication(sys.argv)
    theme_manager = ThemeManager(app, default="dark")
    deskpilot = DeskPilotApp(app, theme_manager=theme_manager)
    deskpilot.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
