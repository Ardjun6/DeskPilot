from __future__ import annotations

from typing import Dict, List

from .base import Action


class FlowAction(Action):
    def __init__(
        self,
        name: str,
        actions: List[Dict[str, object]] | None = None,
        description: str = "",
        icon: str | None = None,
    ) -> None:
        self.name = name
        self.actions = actions or []
        self.description = description
        self.icon = icon

    def execute(self, **kwargs) -> None:
        # TODO: compose and run contained actions sequentially
        return None

    def to_dict(self) -> Dict[str, object]:
        return {
            "type": "flow",
            "name": self.name,
            "actions": self.actions,
            "description": self.description,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "FlowAction":
        actions = data.get("actions") or []
        return cls(
            name=str(data.get("name", "")),
            actions=[dict(a) for a in actions],
            description=str(data.get("description", "")),
            icon=data.get("icon"),
        )
