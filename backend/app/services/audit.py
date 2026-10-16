"""Audit logging helpers.

Records structured audit events for every data mutation so that plugin
registrations and analyses are traceable.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from ..models.analysis import AuditLog


def log_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    detail: Optional[dict[str, Any]] = None,
) -> AuditLog:
    """Insert an audit-log row and return it."""
    entry = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail or {},
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def recent_events(db: Session, limit: int = 50) -> list[AuditLog]:
    from sqlalchemy import desc, select

    stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    return db.execute(stmt).scalars().all()