"""Plugin CRUD + search/list endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from ..schemas.plugin import (
    PluginCreate,
    PluginListRead,
    PluginRead,
    PluginUpdate,
)
from ..services import repository
from ..services.audit import log_event
from .deps import DbSession

router = APIRouter(prefix="/plugins", tags=["plugins"])


@router.post(
    "/", response_model=PluginRead, status_code=status.HTTP_201_CREATED
)
def create_plugin(plugin: PluginCreate, db: DbSession) -> PluginRead:
    existing = repository.get_plugin_by_name(db, plugin.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Plugin '{plugin.name}' is already registered.",
        )
    db_plugin = repository.create_plugin(db, plugin)
    log_event(db, "create", "plugin", db_plugin.id, {"name": db_plugin.name})
    return db_plugin


@router.get("/", response_model=PluginListRead)
def list_plugins(
    db: DbSession,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    plugin_type: Optional[str] = Query(default=None, alias="type"),
    min_score: Optional[int] = Query(default=None, ge=0, le=100, alias="min_score"),
    max_score: Optional[int] = Query(default=None, ge=0, le=100, alias="max_score"),
) -> PluginListRead:
    items, total = repository.list_plugins(
        db,
        page=page,
        per_page=per_page,
        search=search,
        plugin_type=plugin_type,
        min_score=min_score,
        max_score=max_score,
    )
    return PluginListRead(
        items=items, total=total, page=page, per_page=per_page
    )


@router.get("/{plugin_id}", response_model=PluginRead)
def get_plugin(plugin_id: int, db: DbSession) -> PluginRead:
    plugin = repository.get_plugin(db, plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    return plugin


@router.put("/{plugin_id}", response_model=PluginRead)
def update_plugin(plugin_id: int, data: PluginUpdate, db: DbSession) -> PluginRead:
    plugin = repository.update_plugin(db, plugin_id, data)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    log_event(db, "update", "plugin", plugin_id, {"fields": list(data.model_dump(exclude_unset=True).keys())})
    return plugin


@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plugin(plugin_id: int, db: DbSession):
    deleted = repository.delete_plugin(db, plugin_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    log_event(db, "delete", "plugin", plugin_id, {})
    return None