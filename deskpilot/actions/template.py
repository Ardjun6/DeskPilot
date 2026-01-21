from __future__ import annotations

from typing import Dict

from .base import Action


class TemplateAction(Action):
    def __init__(self, name: str, description: str = "", icon: str | None = None) -> None:
        self.name = name
        self.description = description
        self.icon = icon

    def execute(self, **kwargs) -> None:
        # TODO: implement Jinja2 rendering and clipboard copy
        return None

    def to_dict(self) -> Dict[str, object]:
        return {"type": "template", "name": self.name, "description": self.description, "icon": self.icon}

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "TemplateAction":
        return cls(
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            icon=data.get("icon"),
        )
