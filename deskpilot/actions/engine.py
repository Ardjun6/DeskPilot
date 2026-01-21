from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..config.config_manager import ConfigManager
from ..config.models import ActionDef
from ..utils.logging_utils import get_logger
from .results import RunResult
from .steps import CancelToken, Step, StepContext, step_from_def


@dataclass(frozen=True, slots=True)
class ActionPreview:
    action_id: str
    name: str
    lines: List[str]


class ActionEngine:
    """Validate, preview, and execute data-driven actions."""

    def __init__(self, config: ConfigManager) -> None:
        self.config = config
        self.logger = get_logger(__name__)

    def list_actions(self) -> List[ActionDef]:
        return list(self.config.actions.actions)

    def get_action(self, action_id: str) -> Optional[ActionDef]:
        return next((a for a in self.config.actions.actions if a.id == action_id), None)

    def build_steps(self, action: ActionDef) -> List[Step]:
        steps: List[Step] = []
        for s in action.steps:
            steps.append(step_from_def(s.type, dict(s.params)))
        return steps

    def preview(self, action_id: str, inputs: Optional[Dict[str, Any]] = None) -> ActionPreview:
        action = self.get_action(action_id)
        if action is None:
            raise ValueError(f"Unknown action: {action_id}")
        ctx = StepContext(config=self.config, inputs=inputs or {}, dry_run=True)
        steps = self.build_steps(action)
        lines = [step.preview(ctx) for step in steps]
        return ActionPreview(action_id=action.id, name=action.name, lines=lines)

    def run(
        self,
        action_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        *,
        dry_run: bool = False,
        cancel_token: Optional[CancelToken] = None,
    ) -> RunResult:
        action = self.get_action(action_id)
        if action is None:
            raise ValueError(f"Unknown action: {action_id}")

        result = RunResult(status="success")
        token = cancel_token or CancelToken()
        ctx = StepContext(config=self.config, inputs=inputs or {}, dry_run=dry_run, cancel=token)

        try:
            steps = self.build_steps(action)
        except Exception as e:  # noqa: BLE001
            result.add_error(f"Invalid action steps: {e}", exception_type=type(e).__name__)
            return result

        result.add_log("INFO", f"Running action: {action.name}")
        for step in steps:
            if ctx.cancel.cancelled:
                result.status = "cancelled"
                result.add_log("WARNING", "Cancelled", getattr(step, "type", None))
                return result
            try:
                result.add_log("DEBUG", step.preview(ctx), getattr(step, "type", None))
                step.run(ctx, result)
                if result.status == "failed":
                    return result
            except Exception as e:  # noqa: BLE001
                result.add_error(f"Step failed: {e}", getattr(step, "type", None), type(e).__name__)
                return result

        return result

