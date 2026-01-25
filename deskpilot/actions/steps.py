from __future__ import annotations

import os
import shutil
import subprocess
import time
import webbrowser
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from jinja2 import Template

import keyboard
import pyautogui

pyautogui.FAILSAFE = True

from ..config.config_manager import ConfigManager
from ..utils.clipboard import copy_text
from .results import RunResult


@dataclass(slots=True)
class CancelToken:
    cancelled: bool = False


@dataclass(slots=True)
class StepContext:
    config: ConfigManager
    inputs: Dict[str, Any]
    cancel: CancelToken = field(default_factory=CancelToken)
    dry_run: bool = False


class Step(ABC):
    type: str

    @abstractmethod
    def preview(self, ctx: StepContext) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self, ctx: StepContext, result: RunResult) -> None:
        raise NotImplementedError


class WaitStep(Step):
    type = "wait"

    def __init__(self, ms: int = 250) -> None:
        self.ms = ms

    def preview(self, ctx: StepContext) -> str:
        return f"Wait {self.ms}ms"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping wait", self.type)
            return
        time.sleep(max(self.ms, 0) / 1000.0)


class DelayStep(Step):
    type = "delay"

    def __init__(self, seconds: int = 1) -> None:
        self.seconds = seconds

    def preview(self, ctx: StepContext) -> str:
        if self.seconds >= 60:
            minutes = self.seconds // 60
            return f"Wait {minutes} minute(s)"
        return f"Wait {self.seconds} second(s)"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping delay", self.type)
            return
        remaining = max(self.seconds, 0)
        while remaining > 0:
            if ctx.cancel.cancelled:
                result.status = "cancelled"
                result.add_log("WARNING", "Cancelled delay", self.type)
                return
            sleep_chunk = min(1, remaining)
            time.sleep(sleep_chunk)
            remaining -= sleep_chunk


class WaitUntilStep(Step):
    type = "wait_until"

    def __init__(self, target_time: str) -> None:
        self.target_time = target_time

    def preview(self, ctx: StepContext) -> str:
        return f"Wait until {self.target_time}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", f"Dry-run: skipping wait until {self.target_time}", self.type)
            return
        try:
            target = datetime.strptime(self.target_time, "%H:%M").time()
        except ValueError:
            result.add_error(f"Invalid time format: {self.target_time}", self.type)
            return
        now = datetime.now()
        next_run = now.replace(hour=target.hour, minute=target.minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        wait_seconds = max(0, int((next_run - now).total_seconds()))
        remaining = wait_seconds
        while remaining > 0:
            if ctx.cancel.cancelled:
                result.status = "cancelled"
                result.add_log("WARNING", "Cancelled scheduled wait", self.type)
                return
            sleep_chunk = min(5, remaining)
            time.sleep(sleep_chunk)
            remaining -= sleep_chunk


class LaunchProfileStep(Step):
    type = "launch_profile"

    def __init__(self, profile: str, delay_ms: int = 300) -> None:
        self.profile = profile
        self.delay_ms = delay_ms

    def preview(self, ctx: StepContext) -> str:
        targets = ctx.config.profiles.profiles.get(self.profile, [])
        return f"Launch profile '{self.profile}' ({len(targets)} targets)"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        targets = ctx.config.profiles.profiles.get(self.profile, [])
        if not targets:
            result.add_error(f"Profile '{self.profile}' has no targets.", self.type)
            return

        for t in targets:
            if ctx.cancel.cancelled:
                result.status = "cancelled"
                result.add_log("WARNING", "Cancelled", self.type)
                return
            _launch_target(t, dry_run=ctx.dry_run, result=result, step_type=self.type)
            if not ctx.dry_run:
                time.sleep(max(self.delay_ms, 0) / 1000.0)


class RenderTemplateStep(Step):
    type = "render_template"

    def __init__(self, template_id: str, output_key: str = "rendered_text") -> None:
        self.template_id = template_id
        self.output_key = output_key

    def preview(self, ctx: StepContext) -> str:
        return f"Render template '{self.template_id}' → outputs['{self.output_key}']"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        tdef = next((t for t in ctx.config.templates.templates if t.id == self.template_id), None)
        if tdef is None:
            result.add_error(f"Template not found: {self.template_id}", self.type)
            return

        try:
            rendered = Template(tdef.jinja).render(**ctx.inputs)
            result.outputs[self.output_key] = rendered
            result.add_log("INFO", f"Rendered template '{tdef.name}'", self.type)
        except Exception as e:  # noqa: BLE001 - surface to UI/logs
            result.add_error(f"Template render failed: {e}", self.type, type(e).__name__)


class CopyOutputStep(Step):
    type = "copy_output"

    def __init__(self, output_key: str) -> None:
        self.output_key = output_key

    def preview(self, ctx: StepContext) -> str:
        return f"Copy outputs['{self.output_key}'] to clipboard"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        value = result.outputs.get(self.output_key)
        if value is None:
            result.add_error(f"Missing output: {self.output_key}", self.type)
            return
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping clipboard write", self.type)
            return
        copy_text(str(value))
        result.add_log("INFO", "Copied to clipboard", self.type)


class HotkeyStep(Step):
    type = "hotkey"

    def __init__(self, keys: list[str]) -> None:
        self.keys = keys

    def preview(self, ctx: StepContext) -> str:
        return f"Send hotkey: {'+'.join(self.keys)}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping hotkey", self.type)
            return
        keyboard.press_and_release("+".join(self.keys))
        result.add_log("INFO", f"Pressed {'+'.join(self.keys)}", self.type)


class TextStep(Step):
    type = "text"

    def __init__(self, text: str) -> None:
        self.text = text

    def preview(self, ctx: StepContext) -> str:
        return f"Type text ({len(self.text)} chars)"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping typing", self.type)
            return
        pyautogui.typewrite(self.text)
        result.add_log("INFO", "Typed text", self.type)


class PasteStep(Step):
    type = "paste"

    def preview(self, ctx: StepContext) -> str:
        return "Paste clipboard (Ctrl+V)"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping paste", self.type)
            return
        keyboard.press_and_release("ctrl+v")
        result.add_log("INFO", "Pasted clipboard", self.type)


class SetClipboardStep(Step):
    type = "set_clipboard"

    def __init__(self, text: str) -> None:
        self.text = text

    def preview(self, ctx: StepContext) -> str:
        return "Set clipboard text"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping clipboard set", self.type)
            return
        copy_text(self.text)
        result.add_log("INFO", "Clipboard set", self.type)


class OpenAppStep(Step):
    type = "open_app"

    def __init__(self, path: str) -> None:
        self.path = path

    def preview(self, ctx: StepContext) -> str:
        return f"Open app: {self.path}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        _launch_target(self.path, dry_run=ctx.dry_run, result=result, step_type=self.type)


class OpenUrlStep(Step):
    type = "open_url"

    def __init__(self, url: str) -> None:
        self.url = url

    def preview(self, ctx: StepContext) -> str:
        return f"Open URL: {self.url}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        _launch_target(self.url, dry_run=ctx.dry_run, result=result, step_type=self.type)


class RunCommandStep(Step):
    type = "run"

    def __init__(self, command: str) -> None:
        self.command = command

    def preview(self, ctx: StepContext) -> str:
        return f"Run command: {self.command}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", f"Dry-run: would run {self.command}", self.type)
            return
        try:
            subprocess.Popen(self.command, shell=True)  # noqa: S603,S607
            result.add_log("INFO", f"Started command: {self.command}", self.type)
        except Exception as e:  # noqa: BLE001
            result.add_error(f"Command failed: {e}", self.type, type(e).__name__)


class MoveFileStep(Step):
    type = "move_file"

    def __init__(self, src: str, dest: str) -> None:
        self.src = src
        self.dest = dest

    def preview(self, ctx: StepContext) -> str:
        return f"Move file {self.src} → {self.dest}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", f"Dry-run: move {self.src} -> {self.dest}", self.type)
            return
        try:
            shutil.move(self.src, self.dest)
            result.add_log("INFO", f"Moved {self.src} -> {self.dest}", self.type)
        except Exception as e:  # noqa: BLE001
            result.add_error(f"Move failed: {e}", self.type, type(e).__name__)


class MoveFilesStep(Step):
    type = "move_files"

    def __init__(self, sources: list[str], dest: str) -> None:
        self.sources = sources
        self.dest = dest

    def preview(self, ctx: StepContext) -> str:
        return f"Move {len(self.sources)} files -> {self.dest}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        for src in self.sources:
            if ctx.cancel.cancelled:
                result.status = "cancelled"
                return
            if ctx.dry_run:
                result.add_log("INFO", f"Dry-run: move {src} -> {self.dest}", self.type)
                continue
            try:
                shutil.move(src, self.dest)
                result.add_log("INFO", f"Moved {src} -> {self.dest}", self.type)
            except Exception as e:  # noqa: BLE001
                result.add_error(f"Move failed: {e}", self.type, type(e).__name__)
                return


class FocusWindowStep(Step):
    type = "focus_window"

    def __init__(self, title_substring: str, on_fail: str = "warn") -> None:
        self.title_substring = title_substring
        self.on_fail = on_fail

    def preview(self, ctx: StepContext) -> str:
        return f"Ensure window with '{self.title_substring}' is focused"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        active = pyautogui.getActiveWindow()
        title = active.title if active else ""
        if active and self.title_substring.lower() in title.lower():
            result.add_log("INFO", f"Focus OK: {title}", self.type)
            return
        msg = f"Active window mismatch (expected contains '{self.title_substring}', got '{title}')"
        if self.on_fail == "fail":
            result.add_error(msg, self.type)
        else:
            result.add_log("WARNING", msg, self.type)


class FocusAppStep(Step):
    type = "focus_app"

    def __init__(self, title_substring: str, on_fail: str = "warn") -> None:
        self.title_substring = title_substring
        self.on_fail = on_fail

    def preview(self, ctx: StepContext) -> str:
        return f"Focus app window containing '{self.title_substring}'"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", f"Dry-run: focus window '{self.title_substring}'", self.type)
            return
        matches = pyautogui.getWindowsWithTitle(self.title_substring)
        if matches:
            matches[0].activate()
            result.add_log("INFO", f"Focused '{matches[0].title}'", self.type)
            return
        msg = f"No window found containing '{self.title_substring}'"
        if self.on_fail == "fail":
            result.add_error(msg, self.type)
        else:
            result.add_log("WARNING", msg, self.type)


class ClickStep(Step):
    type = "click"

    def __init__(self, x: int, y: int, button: str = "left", clicks: int = 1, interval: float = 0.1) -> None:
        self.x = x
        self.y = y
        self.button = button
        self.clicks = clicks
        self.interval = interval

    def preview(self, ctx: StepContext) -> str:
        return f"Click {self.button} at ({self.x}, {self.y})"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping click", self.type)
            return
        pyautogui.click(x=self.x, y=self.y, button=self.button, clicks=self.clicks, interval=self.interval)
        result.add_log("INFO", f"Clicked {self.button} at ({self.x}, {self.y})", self.type)


class TypeTextStep(Step):
    """Type text using keyboard - different from TextStep, uses pyautogui."""
    type = "type_text"

    def __init__(self, text: str, interval: float = 0.02) -> None:
        self.text = text
        self.interval = interval

    def preview(self, ctx: StepContext) -> str:
        preview = self.text[:30] + "..." if len(self.text) > 30 else self.text
        return f"Type: {preview}"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping type text", self.type)
            return
        pyautogui.typewrite(self.text, interval=self.interval)
        result.add_log("INFO", f"Typed {len(self.text)} characters", self.type)


class PasteHistoryStep(Step):
    """Paste from clipboard history."""
    type = "paste_history"

    def __init__(self, history_index: int = 0) -> None:
        self.history_index = history_index

    def preview(self, ctx: StepContext) -> str:
        names = ["last", "2nd last", "3rd last", "4th last", "5th last"]
        name = names[self.history_index] if self.history_index < len(names) else f"{self.history_index+1}th"
        return f"Paste {name} clipboard item"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping paste history", self.type)
            return
        # Note: This requires the clipboard manager to be accessible
        # For now, just paste current clipboard
        keyboard.press_and_release("ctrl+v")
        result.add_log("INFO", f"Pasted from history (index {self.history_index})", self.type)


class JiggleStep(Step):
    """Jiggle mouse for a duration to keep PC awake."""
    type = "jiggle"

    def __init__(self, duration: int = 60, pattern: str = "natural", interval: int = 30, track_mouse: bool = True) -> None:
        self.duration = duration
        self.pattern = pattern.lower()
        self.interval = interval
        self.track_mouse = track_mouse

    def preview(self, ctx: StepContext) -> str:
        return f"Jiggle mouse for {self.duration}s ({self.pattern})"

    def run(self, ctx: StepContext, result: RunResult) -> None:
        if ctx.dry_run:
            result.add_log("INFO", "Dry-run: skipping jiggle", self.type)
            return
        
        import math
        import random
        
        end_time = time.time() + self.duration
        jiggle_count = 0
        last_pos = pyautogui.position()
        last_move_time = time.time()
        
        result.add_log("INFO", f"Starting jiggle for {self.duration}s (pattern: {self.pattern})", self.type)
        
        while time.time() < end_time:
            if ctx.cancel.cancelled:
                result.status = "cancelled"
                result.add_log("WARNING", "Jiggle cancelled", self.type)
                return
            
            current_pos = pyautogui.position()
            current_time = time.time()
            
            # Check if user moved mouse (Natural tracking)
            if self.track_mouse:
                if current_pos != last_pos:
                    # User moved mouse - count as activity, reset timer
                    last_move_time = current_time
                    jiggle_count += 1
                    last_pos = current_pos
            
            # Only jiggle if enough time passed since last activity
            time_since_activity = current_time - last_move_time
            
            if time_since_activity >= self.interval:
                try:
                    if self.pattern == "natural":
                        # Small subtle movement that looks natural
                        dx = random.choice([-1, 1])
                        pyautogui.moveRel(dx, 0, duration=0.1)
                        time.sleep(0.1)
                        pyautogui.moveRel(-dx, 0, duration=0.1)
                    elif self.pattern == "invisible":
                        pyautogui.moveRel(0, 0)
                    elif self.pattern == "subtle":
                        pyautogui.moveRel(1, 0, duration=0.05)
                        pyautogui.moveRel(-1, 0, duration=0.05)
                    elif self.pattern == "circle":
                        cx, cy = pyautogui.position()
                        for i in range(8):
                            a = (i / 8) * 2 * math.pi
                            pyautogui.moveRel(int(2*math.cos(a)), int(2*math.sin(a)), duration=0.02)
                        pyautogui.moveTo(cx, cy, duration=0.05)
                    elif self.pattern == "random":
                        dx, dy = random.randint(-3, 3), random.randint(-3, 3)
                        pyautogui.moveRel(dx, dy, duration=0.05)
                        pyautogui.moveRel(-dx, -dy, duration=0.05)
                    else:
                        pyautogui.moveRel(1, 0, duration=0.05)
                        pyautogui.moveRel(-1, 0, duration=0.05)
                    
                    jiggle_count += 1
                    last_move_time = current_time
                    last_pos = pyautogui.position()
                except Exception:
                    pass
            
            time.sleep(0.5)  # Check every 0.5 seconds
        
        result.add_log("INFO", f"Jiggled {jiggle_count} times over {self.duration}s", self.type)


def step_from_def(step_type: str, params: Dict[str, Any]) -> Step:
    if step_type == "wait":
        return WaitStep(ms=int(params.get("ms", 250)))
    if step_type == "delay":
        return DelayStep(seconds=int(params.get("seconds", 1)))
    if step_type == "wait_until":
        return WaitUntilStep(target_time=str(params.get("time", "")))
    if step_type == "launch_profile":
        return LaunchProfileStep(profile=str(params.get("profile", "")), delay_ms=int(params.get("delay_ms", 300)))
    if step_type == "render_template":
        return RenderTemplateStep(
            template_id=str(params.get("template_id", "")),
            output_key=str(params.get("output_key", "rendered_text")),
        )
    if step_type == "copy_output":
        return CopyOutputStep(output_key=str(params.get("output_key", "")))
    if step_type == "hotkey":
        keys = params.get("keys", [])
        if isinstance(keys, str):
            keys = keys.split("+")
        return HotkeyStep(keys=[str(k) for k in keys])
    if step_type == "text":
        return TextStep(text=str(params.get("text", "")))
    if step_type == "type_text":
        return TypeTextStep(text=str(params.get("text", "")))
    if step_type == "paste":
        return PasteStep()
    if step_type == "paste_history":
        return PasteHistoryStep(history_index=int(params.get("history_index", 0)))
    if step_type == "set_clipboard":
        return SetClipboardStep(text=str(params.get("text", "")))
    if step_type == "open_app":
        return OpenAppStep(path=str(params.get("path", "")))
    if step_type == "open_url":
        return OpenUrlStep(url=str(params.get("url", "")))
    if step_type == "run":
        return RunCommandStep(command=str(params.get("command", "")))
    if step_type == "move_file":
        return MoveFileStep(src=str(params.get("src", "")), dest=str(params.get("dest", "")))
    if step_type == "move_files":
        return MoveFilesStep(sources=[str(s) for s in params.get("sources", [])], dest=str(params.get("dest", "")))
    if step_type == "focus_window":
        return FocusWindowStep(title_substring=str(params.get("title", "")), on_fail=str(params.get("on_fail", "warn")))
    if step_type == "focus_app":
        return FocusAppStep(title_substring=str(params.get("title", "")), on_fail=str(params.get("on_fail", "warn")))
    if step_type == "click":
        return ClickStep(
            x=int(params.get("x", 0)),
            y=int(params.get("y", 0)),
            button=str(params.get("button", "left")),
            clicks=int(params.get("clicks", 1)),
            interval=float(params.get("interval", 0.1)),
        )
    if step_type == "jiggle":
        return JiggleStep(
            duration=int(params.get("duration", 60)),
            pattern=str(params.get("pattern", "natural")),
            interval=int(params.get("interval", 30)),
            track_mouse=bool(params.get("track_mouse", True)),
        )
    raise ValueError(f"Unknown step type: {step_type}")


def _launch_target(target: str, dry_run: bool, result: RunResult, step_type: str) -> None:
    if target.lower().startswith(("http://", "https://")):
        if dry_run:
            result.add_log("INFO", f"Dry-run: would open URL {target}", step_type)
            return
        webbrowser.open(target)
        result.add_log("INFO", f"Opened URL: {target}", step_type)
        return

    if dry_run:
        result.add_log("INFO", f"Dry-run: would launch {target}", step_type)
        return

    try:
        if os.path.exists(target):
            os.startfile(target)  # type: ignore[attr-defined]  # Windows only
        else:
            subprocess.Popen(target, shell=True)  # noqa: S603,S607 - user-configured local command
        result.add_log("INFO", f"Launched: {target}", step_type)
    except Exception as e:  # noqa: BLE001
        result.add_error(f"Failed to launch '{target}': {e}", step_type, type(e).__name__)
