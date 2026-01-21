from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path


def build_exe() -> int:
    """Build a Windows executable using PyInstaller."""
    if importlib.util.find_spec("PyInstaller") is None:
        print("PyInstaller is required. Install with: pip install pyinstaller")
        return 1

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
