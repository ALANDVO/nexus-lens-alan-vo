"""Data access layer — repository pattern over SQLAlchemy."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select, update, asc, desc, func
from sqlalchemy.orm import Session, selectinload

from ..core.database import Base
from ..models.analysis import AnalysisResult, AuditLog, Finding
from ..models.plugin import Plugin
from ..schemas.plugin import PluginCreate, PluginUpdate
from ..services.conformance import AnalysisResult as AnalysisData, Finding as FindingData


# --- Plugins ---

def create_plugin(db: Session, data: PluginCreate) -> Plugin:
    plugin = Plugin(
        name=data.name,
        description=data.description,
        source=data.source,
        plugin_type=data.plugin_type.value if hasattr(data.plugin_type, "value") else data.plugin_type,
        manifest=data.manifest,
    )
    db.add(plugin)
    db.commit()
    db.refresh(plugin)
    return plugin


def get_plugin(db: Session, plugin_id: int) -> Optional[Plugin]:
    return db.get(Plugin, plugin_id)


def get_plugin_by_name(db: Session, name: str) -> Optional[Plugin]:
    stmt = select(Plugin).where(Plugin.name == name)
    return db.execute(stmt).scalar_one_or_none()


def list_plugins(
    db: Session,
    *,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    plugin_type: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
) -> tuple[list[Plugin], int]:
    stmt = select(Plugin).order_by(asc(Plugin.name))
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            func.lower(Plugin.name).like(pattern)
            | func.lower(Plugin.description).like(pattern)
            | func.lower(Plugin.source).like(pattern)
        )
    if plugin_type:
        stmt = stmt.where(Plugin.plugin_type == plugin_type)
    if min_score is not None:
        stmt = stmt.where(Plugin.latest_score >= min_score)
    if max_score is not None:
        stmt = stmt.where(Plugin.latest_score <= max_score)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    offset = (page - 1) * per_page
    items = db.execute(stmt.offset(offset).limit(per_page)).scalars().all()
    return items, total


def update_plugin(db: Session, plugin_id: int, data: PluginUpdate) -> Optional[Plugin]:
    plugin = db.get(Plugin, plugin_id)
    if plugin is None:
        return None
    values = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if "plugin_type" in values and hasattr(values["plugin_type"], "value"):
        values["plugin_type"] = values["plugin_type"].value
    if values:
        db.execute(
            update(Plugin).where(Plugin.id == plugin_id).values(**values)
        )
        db.commit()
        db.refresh(plugin)
    return plugin


def delete_plugin(db: Session, plugin_id: int) -> bool:
    plugin = db.get(Plugin, plugin_id)
    if plugin is None:
        return False
    db.delete(plugin)
    db.commit()
    return True


# --- Analyses ---

def create_analysis(db: Session, plugin_id: int, result: AnalysisData) -> AnalysisResult:
    analysis = AnalysisResult(
        plugin_id=plugin_id,
        score=result.score,
        band=result.band,
        checks_run=result.checks_run,
    )
    db.add(analysis)
    db.flush()

    for f in result.findings:
        db.add(
            Finding(
                analysis_id=analysis.id,
                check_id=f.check_id,
                severity=f.severity.value,
                message=f.message,
                evidence=f.evidence,
            )
        )

    # Update plugin's latest summary.
    db.execute(
        update(Plugin)
        .where(Plugin.id == plugin_id)
        .values(latest_score=result.score, latest_band=result.band)
    )

    db.commit()

    # Reload with findings eagerly loaded (selectinload is reliable after commit).
    stmt = (
        select(AnalysisResult)
        .options(selectinload(AnalysisResult.findings))
        .where(AnalysisResult.id == analysis.id)
    )
    return db.execute(stmt).scalar_one()


def get_analysis(db: Session, analysis_id: int) -> Optional[AnalysisResult]:
    stmt = (
        select(AnalysisResult)
        .options(selectinload(AnalysisResult.findings))
        .where(AnalysisResult.id == analysis_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_analyses(db: Session, plugin_id: int) -> list[AnalysisResult]:
    stmt = (
        select(AnalysisResult)
        .where(AnalysisResult.plugin_id == plugin_id)
        .order_by(desc(AnalysisResult.created_at))
    )
    return db.execute(stmt).scalars().all()


# --- Audit ---

def create_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    detail: Optional[dict[str, Any]] = None,
) -> AuditLog:
    log = AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, detail=detail or {})
    db.add(log)
    db.commit()
    db.refresh(log)
    return log