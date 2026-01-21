from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional


RunStatus = Literal["success", "failed", "cancelled"]


@dataclass(slots=True)
class LogEntry:
    level: str
    message: str
    step_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class ActionError:
    message: str
    step_type: Optional[str] = None
    exception_type: Optional[str] = None


@dataclass(slots=True)
class RunResult:
    status: RunStatus = "success"
    logs: List[LogEntry] = field(default_factory=list)
    errors: List[ActionError] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)

    def add_log(self, level: str, message: str, step_type: Optional[str] = None) -> None:
        self.logs.append(LogEntry(level=level, message=message, step_type=step_type))

    def add_error(self, message: str, step_type: Optional[str] = None, exception_type: Optional[str] = None) -> None:
        self.errors.append(ActionError(message=message, step_type=step_type, exception_type=exception_type))
        self.status = "failed"

