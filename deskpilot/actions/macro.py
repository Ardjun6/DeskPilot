from __future__ import annotations

from typing import Dict, List

from .base import Action


class MacroAction(Action):
    def __init__(
        self,
        name: str,
        steps: List[Dict[str, object]] | None = None,
        description: str = "",
        icon: str | None = None,
    ) -> None:
        self.name = name
        self.steps = steps or []
        self.description = description
        self.icon = icon

    def execute(self, **kwargs) -> None:
        # TODO: implement macro playback with safety
        return None

    def to_dict(self) -> Dict[str, object]:
        return {
            "type": "macro",
            "name": self.name,
            "steps": self.steps,
            "description": self.description,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "MacroAction":
        steps = data.get("steps") or []
        return cls(
            name=str(data.get("name", "")),
            steps=[dict(s) for s in steps],
            description=str(data.get("description", "")),
            icon=data.get("icon"),
        )
