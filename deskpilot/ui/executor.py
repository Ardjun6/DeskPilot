from __future__ import annotations

from typing import Any, Dict, Optional

from PySide6.QtCore import QThread, Signal

from ..actions.engine import ActionEngine
from ..actions.macro_engine import MacroEngine
from ..actions.results import RunResult
from ..actions.steps import CancelToken


class ExecutionWorker(QThread):
    """Run actions/macros in a background thread with cancellation."""

    finished_with_result = Signal(RunResult)

    def __init__(
        self,
        engine: ActionEngine,
        action_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        *,
        dry_run: bool = False,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.action_id = action_id
        self.inputs = inputs or {}
        self.dry_run = dry_run
        self.cancel_token = CancelToken()

    def request_cancel(self) -> None:
        self.cancel_token.cancelled = True

    def run(self) -> None:
        result = self.engine.run(
            self.action_id,
            inputs=self.inputs,
            dry_run=self.dry_run,
            cancel_token=self.cancel_token,
        )
        self.finished_with_result.emit(result)


class MacroExecutionWorker(QThread):
    finished_with_result = Signal(RunResult)

    def __init__(
        self,
        engine: MacroEngine,
        macro_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        *,
        dry_run: bool = False,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.macro_id = macro_id
        self.inputs = inputs or {}
        self.dry_run = dry_run
        self.cancel_token = CancelToken()

    def request_cancel(self) -> None:
        self.cancel_token.cancelled = True

    def run(self) -> None:
        result = self.engine.run(
            self.macro_id,
            inputs=self.inputs,
            dry_run=self.dry_run,
            cancel_token=self.cancel_token,
        )
        self.finished_with_result.emit(result)
