"""Analysis result, finding, and audit-log models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    plugin_id = Column(
        Integer, ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score = Column(Integer, nullable=False)
    band = Column(String(20), nullable=False)
    # Ordered list of check IDs that were executed.
    checks_run = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plugin = relationship("Plugin", back_populates="analyses")
    findings = relationship(
        "Finding",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="Finding.id",
    )


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    analysis_id = Column(
        Integer,
        ForeignKey("analysis_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    check_id = Column(String(60), nullable=False)
    severity = Column(String(10), nullable=False)  # pass | warn | fail
    message = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)

    analysis = relationship("AnalysisResult", back_populates="findings")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    action = Column(String(30), nullable=False)  # create | update | delete | analyze
    entity_type = Column(String(30), nullable=False)  # plugin | analysis
    entity_id = Column(Integer, nullable=True)
    detail = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
