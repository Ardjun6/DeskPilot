from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Type, TypeVar

ActionT = TypeVar("ActionT", bound="Action")


class Action(ABC):
    """Abstract base class for executable actions."""

    name: str
    description: str
    icon: str | None

    @abstractmethod
    def execute(self, **kwargs) -> None:
        """Run the action."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Dict[str, object]:
        """Serialize action to a dictionary."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[ActionT], data: Dict[str, object]) -> ActionT:
        """Deserialize action from a dictionary."""
        raise NotImplementedError


class ActionRegistry:
    """Registry to map action type names to classes."""

    def __init__(self) -> None:
        self._registry: Dict[str, Type[Action]] = {}

    def register(self, key: str, action_cls: Type[Action]) -> None:
        self._registry[key] = action_cls

    def create(self, key: str, data: Dict[str, object]) -> Action:
        action_cls = self._registry.get(key)
        if action_cls is None:
            raise ValueError(f"Unknown action type: {key}")
        return action_cls.from_dict(data)

    def keys(self) -> list[str]:
        return list(self._registry.keys())
