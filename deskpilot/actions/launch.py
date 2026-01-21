from __future__ import annotations

from typing import Dict, List

from .base import Action


class LaunchAction(Action):
    def __init__(
        self,
        name: str,
        targets: List[str] | None = None,
        description: str = "",
        icon: str | None = None,
    ) -> None:
        self.name = name
        self.targets = targets or []
        self.description = description
        self.icon = icon

    def execute(self, **kwargs) -> None:
        # TODO: implement subprocess/os.startfile/webbrowser launches
        return None

    def to_dict(self) -> Dict[str, object]:
        return {
            "type": "launch",
            "name": self.name,
            "targets": list(self.targets),
            "description": self.description,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "LaunchAction":
        targets = data.get("targets") or []
        return cls(
            name=str(data.get("name", "")),
            targets=[str(t) for t in targets],
            description=str(data.get("description", "")),
            icon=data.get("icon"),
        )
