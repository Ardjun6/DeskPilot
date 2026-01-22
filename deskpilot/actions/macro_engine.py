from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..config.config_manager import ConfigManager
from ..config.models import MacroDef
from ..utils.logging_utils import get_logger
from .results import RunResult
from .steps import CancelToken, DelayStep, FocusAppStep, StepContext, WaitUntilStep, step_from_def


class MacroEngine:
    """Validate, preview, and run macros defined in macros.json."""

    def __init__(self, config: ConfigManager) -> None:
        self.config = config
        self.logger = get_logger(__name__)

    def list_macros(self) -> List[MacroDef]:
        return [m for m in self.config.macros.macros if m.enabled]

    def get_macro(self, macro_id: str) -> Optional[MacroDef]:
        return next((m for m in self.config.macros.macros if m.id == macro_id), None)

    def build_steps(self, macro: MacroDef, inputs: Dict[str, Any]):
        def resolve(value):
            if isinstance(value, str):
                try:
                    return value.format(**inputs)
                except Exception:
                    return value
            if isinstance(value, list):
                return [resolve(v) for v in value]
            if isinstance(value, dict):
                return {k: resolve(v) for k, v in value.items()}
            return value

        steps = [step_from_def(s.type, resolve(dict(s.params))) for s in macro.steps]
        schedule_steps = []
        if macro.schedule_time:
            schedule_steps.append(WaitUntilStep(target_time=macro.schedule_time))
        if macro.schedule_delay:
            schedule_steps.append(DelayStep(seconds=macro.schedule_delay))
        if macro.app_title:
            schedule_steps.append(FocusAppStep(title_substring=macro.app_title))
        return schedule_steps + steps

    def run(
        self,
        macro_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        *,
        dry_run: bool = False,
        cancel_token: Optional[CancelToken] = None,
    ) -> RunResult:
        macro = self.get_macro(macro_id)
        if macro is None:
            raise ValueError(f"Unknown macro: {macro_id}")
        result = RunResult(status="success")
        token = cancel_token or CancelToken()
        resolved_inputs = inputs or {}
        ctx = StepContext(config=self.config, inputs=resolved_inputs, dry_run=dry_run, cancel=token)
        try:
            steps = self.build_steps(macro, resolved_inputs)
        except Exception as e:  # noqa: BLE001
            result.add_error(f"Invalid macro steps: {e}", exception_type=type(e).__name__)
            return result

        result.add_log("INFO", f"Running macro: {macro.name}")
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

    def preview(self, macro_id: str) -> List[str]:
        macro = self.get_macro(macro_id)
        if macro is None:
            return []
        ctx = StepContext(config=self.config, inputs={}, dry_run=True, cancel=CancelToken())
        return [step.preview(ctx) for step in self.build_steps(macro)]
