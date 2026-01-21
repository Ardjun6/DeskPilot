from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .models import ActionsFile, MacrosFile, ProfilesFile, TemplatesFile


class ConfigManager:
    """Manage loading and saving DeskPilot configuration (Windows/local-first).

    Supports:
    - Split config files (actions.yaml, templates.yaml, profiles.yaml)
    - Portable mode (config/ next to the executable)
    - Config versioning/migrations (starting at v1)
    - Example generation on first run
    """

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = base_dir or self._detect_base_dir()
        self.config_dir = self.base_dir / "config"

        self.actions_path = self.config_dir / "actions.yaml"
        self.templates_path = self.config_dir / "templates.yaml"
        self.profiles_path = self.config_dir / "profiles.yaml"
        self.macros_path = self.config_dir / "macros.json"

        self.data: Dict[str, Any] = {}
        self.actions: ActionsFile = ActionsFile()
        self.templates: TemplatesFile = TemplatesFile()
        self.profiles: ProfilesFile = ProfilesFile()
        self.macros: MacrosFile = MacrosFile()

    def ensure_loaded(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_files_exist()

        self.actions = ActionsFile.model_validate(self._load_yaml(self.actions_path))
        self.templates = TemplatesFile.model_validate(self._load_yaml(self.templates_path))
        self.profiles = ProfilesFile.model_validate(self._load_yaml(self.profiles_path))
        self.macros = MacrosFile.model_validate(self._load_json(self.macros_path))

        self._migrate_if_needed()
        self._refresh_legacy_view()

    def _detect_base_dir(self) -> Path:
        """Prefer portable config next to the .exe; otherwise use user home."""
        exe_path = Path(sys.executable).resolve()
        portable_dir = exe_path.parent
        if (portable_dir / "config").exists():
            return portable_dir
        return Path.home() / ".deskpilot"

    def _ensure_files_exist(self) -> None:
        if not self.actions_path.exists():
            self._write_yaml(self.actions_path, self._example_actions_yaml())
        if not self.templates_path.exists():
            self._write_yaml(self.templates_path, self._example_templates_yaml())
        if not self.profiles_path.exists():
            self._write_yaml(self.profiles_path, self._example_profiles_yaml())
        if not self.macros_path.exists():
            self._write_json(self.macros_path, self._example_macros_json())

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def _write_yaml(self, path: Path, data: Dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _migrate_if_needed(self) -> None:
        # v1 is current; migrations are placeholders for future versions.
        # Keep this function so we can evolve schemas without breaking users.
        return None

    def save_all(self) -> None:
        self._write_yaml(self.actions_path, json.loads(self.actions.model_dump_json()))
        self._write_yaml(self.templates_path, json.loads(self.templates.model_dump_json()))
        self._write_yaml(self.profiles_path, json.loads(self.profiles.model_dump_json()))
        self._write_json(self.macros_path, json.loads(self.macros.model_dump_json()))
        self._refresh_legacy_view()

    def _refresh_legacy_view(self) -> None:
        """Legacy dict view (used by early UI code)."""
        self.data = {
            "actions": [a.model_dump() for a in self.actions.actions],
            "templates": [t.model_dump() for t in self.templates.templates],
            "profiles": self.profiles.profiles,
            "macros": [m.model_dump() for m in self.macros.macros],
        }

    def _example_profiles_yaml(self) -> Dict[str, Any]:
        return {
            "config_version": 1,
            "profiles": {
                "Work": [
                    "C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe",
                    "https://outlook.office.com/",
                    "https://calendar.google.com/",
                ],
                "Study": ["https://www.google.com/search?q=study+plan", "https://www.notion.so/"],
            },
        }

    def _example_templates_yaml(self) -> Dict[str, Any]:
        return {
            "config_version": 1,
            "templates": [
                {
                    "id": "email_basic",
                    "name": "Email: Professional (basic)",
                    "category": "email",
                    "tone_presets": ["Neutral", "Friendly", "Formal", "Direct"],
                    "fields": [
                        {"key": "recipient", "label": "Recipient", "type": "text", "required": True},
                        {"key": "context", "label": "Context", "type": "multiline", "required": True},
                        {"key": "goal", "label": "Goal", "type": "multiline", "required": True},
                        {"key": "tone", "label": "Tone", "type": "choice", "required": True, "choices": ["Neutral", "Friendly", "Formal", "Direct"], "default": "Neutral"},
                    ],
                    "jinja": (
                        "Hi {{ recipient }},\n\n"
                        "{{ context }}\n\n"
                        "My goal is: {{ goal }}\n\n"
                        "{% if tone == 'Formal' %}Sincerely,{% elif tone == 'Friendly' %}Thanks!{% elif tone == 'Direct' %}Regards,{% else %}Best,{% endif %}\n"
                        "{{ sender | default('') }}"
                    ),
                    "outputs": {"clipboard": True, "save_file": False, "open_mail": False},
                }
            ],
        }

    def _example_actions_yaml(self) -> Dict[str, Any]:
        return {
            "config_version": 1,
            "actions": [
                {
                    "id": "work_profile",
                    "name": "Launch: Work profile",
                    "description": "Open your Work apps/URLs from profiles.yaml",
                    "tags": ["launch", "work"],
                    "favorite": True,
                    "steps": [{"type": "launch_profile", "params": {"profile": "Work", "delay_ms": 400}}],
                },
                {
                    "id": "study_profile",
                    "name": "Launch: Study profile",
                    "description": "Open your Study URLs from profiles.yaml",
                    "tags": ["launch", "study"],
                    "steps": [{"type": "launch_profile", "params": {"profile": "Study", "delay_ms": 400}}],
                },
                {
                    "id": "template_email_basic",
                    "name": "Template: Email (basic) → Clipboard",
                    "description": "Fill a form, render Jinja template, copy to clipboard",
                    "tags": ["template", "email"],
                    "favorite": True,
                    "steps": [{"type": "render_template", "params": {"template_id": "email_basic"}}, {"type": "copy_output", "params": {"output_key": "rendered_text"}}],
                },
            ],
        }

    def _example_macros_json(self) -> Dict[str, Any]:
        return {
            "config_version": 1,
            "macros": [
                {
                    "id": "quick_note",
                    "name": "Quick Note",
                    "description": "Open Notepad and paste clipboard",
                    "category": "utility",
                    "enabled": True,
                    "hotkey": None,
                    "safety": "safe",
                    "steps": [
                        {"type": "open_app", "params": {"path": "notepad.exe"}},
                        {"type": "wait", "params": {"ms": 500}},
                        {"type": "paste", "params": {}},
                    ],
                },
                {
                    "id": "research_tabs",
                    "name": "Research Tabs",
                    "description": "Open docs and search page",
                    "category": "browser",
                    "enabled": True,
                    "hotkey": None,
                    "safety": "safe",
                    "steps": [
                        {"type": "open_url", "params": {"url": "https://www.google.com"}},
                        {"type": "open_url", "params": {"url": "https://stackoverflow.com"}},
                    ],
                },
            ],
        }
