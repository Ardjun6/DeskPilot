from __future__ import annotations

import os
from pathlib import Path
from typing import List, NamedTuple


class DiscoveredApp(NamedTuple):
    name: str
    path: str


START_MENU_DIRS = [
    Path(os.environ.get("PROGRAMDATA", "")) / r"Microsoft\Windows\Start Menu\Programs",
    Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs",
]

PROGRAM_DIRS = [
    Path(os.environ.get("PROGRAMFILES", "")),
    Path(os.environ.get("PROGRAMFILES(X86)", "")),
]


def discover_apps(limit: int = 300) -> List[DiscoveredApp]:
    apps: List[DiscoveredApp] = []

    def add_app(path: Path) -> None:
        name = path.stem
        apps.append(DiscoveredApp(name=name, path=str(path)))

    for base in START_MENU_DIRS:
        if base.exists():
            for exe in base.rglob("*.lnk"):
                add_app(exe)
                if len(apps) >= limit:
                    return apps

    for base in PROGRAM_DIRS:
        if base.exists():
            depth = 2
            for exe in base.glob("**/*.exe"):
                add_app(exe)
                if len(apps) >= limit:
                    return apps
                # simple depth limit
                if len(exe.relative_to(base).parts) > depth:
                    continue

    # de-duplicate by path
    unique = {}
    for a in apps:
        unique[a.path] = a
    return list(unique.values())
