"""Conformance analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
import json

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


@router.get("/analyses/{analysis_id}/export")
def export_analysis(analysis_id: int, db: DbSession):
    """Export a full analysis report as JSON for review."""
    analysis = repository.get_analysis(db, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    plugin = repository.get_plugin(db, analysis.plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Associated plugin not found.")

    export_data = {
        "type": "analysis_report",
        "plugin": {
            "id": plugin.id,
            "name": plugin.name,
            "description": plugin.description,
            "source": plugin.source,
            "plugin_type": plugin.plugin_type,
            "manifest": plugin.manifest,
        },
        "analysis": {
            "id": analysis.id,
            "score": analysis.score,
            "band": analysis.band,
            "checks_run": analysis.checks_run,
            "created_at": analysis.created_at.isoformat(),
            "findings": [
                {
                    "check_id": f.check_id,
                    "severity": f.severity,
                    "message": f.message,
                    "evidence": f.evidence,
                }
                for f in analysis.findings
            ],
        },
    }

    json_bytes = json.dumps(export_data, indent=2).encode("utf-8")
    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="analysis-{analysis_id}-report.json"'
        },
    )


@router.get("/{plugin_id}/export")
def export_plugin(plugin_id: int, db: DbSession):
    """Export a plugin with its latest analysis as JSON for review."""
    plugin = repository.get_plugin(db, plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found.")

    analyses = repository.list_analyses(db, plugin_id)
    latest_analysis = analyses[0] if analyses else None

    export_data = {
        "type": "plugin_report",
        "plugin": {
            "id": plugin.id,
            "name": plugin.name,
            "description": plugin.description,
            "source": plugin.source,
            "plugin_type": plugin.plugin_type,
            "manifest": plugin.manifest,
            "latest_score": plugin.latest_score,
            "latest_band": plugin.latest_band,
            "created_at": plugin.created_at.isoformat(),
            "updated_at": plugin.updated_at.isoformat(),
        },
        "latest_analysis": (
            {
                "id": latest_analysis.id,
                "score": latest_analysis.score,
                "band": latest_analysis.band,
                "checks_run": latest_analysis.checks_run,
                "created_at": latest_analysis.created_at.isoformat(),
                "findings": [
                    {
                        "check_id": f.check_id,
                        "severity": f.severity,
                        "message": f.message,
                        "evidence": f.evidence,
                    }
                    for f in latest_analysis.findings
                ],
            }
            if latest_analysis
            else None
        ),
    }

    json_bytes = json.dumps(export_data, indent=2).encode("utf-8")
    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="plugin-{plugin_id}-report.json"'
        },
    )
