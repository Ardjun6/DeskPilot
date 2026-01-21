from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_CONFIG_DIR = Path.home() / ".deskpilot"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"


class ConfigManager:
    """Manage loading and saving DeskPilot configuration."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_CONFIG_FILE
        self.data: Dict[str, Any] = {}

    def ensure_loaded(self) -> None:
        if not self.path.exists():
            self._initialize_defaults()
        self.data = self._load()

    def _initialize_defaults(self) -> None:
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        defaults = {
            "profiles": {"Work": [], "Study": []},
            "templates": {},
            "macros": {},
            "flows": {},
            "hotkeys": {},
            "settings": {},
        }
        self._save(defaults)

    def _load(self) -> Dict[str, Any]:
        if self.path.suffix.lower() == ".json":
            return json.loads(self.path.read_text(encoding="utf-8"))
        return yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}

    def _save(self, data: Dict[str, Any]) -> None:
        if self.path.suffix.lower() == ".json":
            self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        else:
            yaml.safe_dump(data, self.path.open("w", encoding="utf-8"), default_flow_style=False)

    def save(self) -> None:
        self._save(self.data)
