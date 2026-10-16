"""Conformance analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.plugin import AnalysisRead
from ..services import repository
from ..services.audit import log_event
from ..services.conformance import analyze
from .deps import DbSession

router = APIRouter(prefix="/plugins", tags=["analysis"])


@router.post("/{plugin_id}/analyze", response_model=AnalysisRead)
def run_analysis(plugin_id: int, db: DbSession) -> AnalysisRead:
    plugin = repository.get_plugin(db, plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found.")

    result = analyze(plugin.manifest)
    analysis = repository.create_analysis(db, plugin_id, result)
    log_event(
        db,
        "analyze",
        "analysis",
        analysis.id,
        {
            "plugin_id": plugin_id,
            "score": result.score,
            "band": result.band,
            "findings": len(result.findings),
        },
    )
    return analysis


@router.get("/analyses/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: int, db: DbSession) -> AnalysisRead:
    analysis = repository.get_analysis(db, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis


@router.get("/{plugin_id}/analyses", response_model=list)
def list_analyses(plugin_id: int, db: DbSession):
    plugin = repository.get_plugin(db, plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found.")
    analyses = repository.list_analyses(db, plugin_id)
    # Return summaries (omit findings list to keep response slim).
    return [
        {
            "id": a.id,
            "plugin_id": a.plugin_id,
            "score": a.score,
            "band": a.band,
            "checks_run": a.checks_run,
            "created_at": a.created_at.isoformat(),
        }
        for a in analyses
    ]