from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ConfigVersion = Literal[1]


class FieldDef(BaseModel):
    key: str
    label: str
    type: Literal["text", "multiline", "choice"] = "text"
    required: bool = True
    default: Optional[str] = None
    choices: List[str] = Field(default_factory=list)


class TemplateDef(BaseModel):
    id: str
    name: str
    category: str = "general"
    tone_presets: List[str] = Field(default_factory=lambda: ["Neutral", "Friendly", "Formal", "Direct"])
    fields: List[FieldDef] = Field(default_factory=list)
    jinja: str
    outputs: Dict[str, Any] = Field(default_factory=lambda: {"clipboard": True})
    hotkey: Optional[str] = None


class StepDef(BaseModel):
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class ActionDef(BaseModel):
    id: str
    name: str
    description: str = ""
    icon: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    favorite: bool = False
    hotkey: Optional[str] = None
    steps: List[StepDef] = Field(default_factory=list)


class ProfilesFile(BaseModel):
    config_version: ConfigVersion = 1
    profiles: Dict[str, List[str]] = Field(default_factory=dict)


class TemplatesFile(BaseModel):
    config_version: ConfigVersion = 1
    templates: List[TemplateDef] = Field(default_factory=list)


class ActionsFile(BaseModel):
    config_version: ConfigVersion = 1
    actions: List[ActionDef] = Field(default_factory=list)


MacroSafety = Literal["safe", "confirm", "danger"]


class MacroStepDef(BaseModel):
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class MacroDef(BaseModel):
    id: str
    name: str
    description: str = ""
    category: str = "general"
    enabled: bool = True
    hotkey: Optional[str] = None
    safety: MacroSafety = "safe"
    steps: List[MacroStepDef] = Field(default_factory=list)
    schedule_time: Optional[str] = None
    schedule_delay: Optional[int] = None
    app_title: Optional[str] = None


class MacrosFile(BaseModel):
    config_version: ConfigVersion = 1
    macros: List[MacroDef] = Field(default_factory=list)


class LauncherStepDef(BaseModel):
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class LauncherDef(BaseModel):
    id: str
    name: str
    description: str = ""
    hotkey: Optional[str] = None
    schedule_time: Optional[str] = None
    schedule_delay: Optional[int] = None
    steps: List[LauncherStepDef] = Field(default_factory=list)


class LaunchersFile(BaseModel):
    config_version: ConfigVersion = 1
    launchers: List[LauncherDef] = Field(default_factory=list)
