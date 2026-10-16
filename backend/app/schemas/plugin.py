"""Pydantic request/response schemas for plugins and analyses."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class PluginType(str, Enum):
    lsp = "lsp"
    mcp = "mcp"
    hook = "hook"
    other = "other"

    @classmethod
    def _missing_(cls, value):
        return cls.other


# --- Plugin ---

class PluginBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1, max_length=200)
    plugin_type: PluginType = PluginType.other
    manifest: dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True}


class PluginCreate(PluginBase):
    pass


class PluginUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, min_length=1)
    source: Optional[str] = Field(default=None, max_length=200)
    plugin_type: Optional[PluginType] = None
    manifest: Optional[dict[str, Any]] = None


class PluginRead(PluginBase):
    id: int
    latest_score: Optional[int] = None
    latest_band: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"use_enum_values": True, "from_attributes": True}


# --- Finding ---

class FindingRead(BaseModel):
    check_id: str
    severity: str
    message: str
    evidence: dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# --- Analysis ---

class AnalysisRead(BaseModel):
    id: int
    plugin_id: int
    score: int
    band: str
    checks_run: list[str]
    findings: list[FindingRead]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisSummaryRead(BaseModel):
    id: int
    plugin_id: int
    score: int
    band: str
    checks_run: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Pagination ---

class PluginListRead(BaseModel):
    items: list[PluginRead]
    total: int
    page: int
    per_page: int