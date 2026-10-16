"""Plugin domain model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base

# Plugin type vocabulary (mirrors marketplace config shapes).
PLUGIN_TYPES = ("lsp", "mcp", "hook", "other")


class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=False)
    # GitHub owner/repo reference or external URL.
    source = Column(String(200), nullable=False)
    plugin_type = Column(String(20), nullable=False, default="other")
    # Full manifest dict: marketplace.json entry + .lsp.json + plugin.json merged.
    manifest = Column(JSON, nullable=False)

    latest_score = Column(Integer, nullable=True)
    latest_band = Column(String(20), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    analyses = relationship(
        "AnalysisResult",
        back_populates="plugin",
        cascade="all, delete-orphan",
        order_by="AnalysisResult.created_at.desc()",
    )

