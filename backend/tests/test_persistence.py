"""Persistence + audit-log tests (cross-session verification)."""

from __future__ import annotations

from app.core.database import SessionLocal
from app.models.analysis import AnalysisResult, AuditLog, Finding
from app.models.plugin import Plugin
from app.schemas.plugin import PluginCreate
from app.services import repository
from app.services.audit import log_event
from app.services.conformance import analyze
from sample_data import CLEAN_MANIFEST, INCOMPLETE_MANIFEST


def test_create_and_retrieve_persistence(db_session):
    """A plugin created in one session is visible in a fresh session."""
    data = PluginCreate(
        name="persist-plugin",
        description="A plugin created to verify SQLite persistence.",
        source="owner/repo",
        plugin_type="mcp",
        manifest={"name": "persist-plugin", "source": "owner/repo", "plugin_type": "mcp"},
    )
    plugin = repository.create_plugin(db_session, data)
    plugin_id = plugin.id

    fresh = SessionLocal()
    try:
        retrieved = repository.get_plugin(fresh, plugin_id)
        assert retrieved is not None
        assert retrieved.name == "persist-plugin"
        assert retrieved.source == "owner/repo"
    finally:
        fresh.close()


def test_analysis_findings_persisted(db_session):
    """Findings with evidence survive a cross-session read."""
    data = PluginCreate(
        name="analyze-persist",
        description="Plugin for analysis persistence check.",
        source="owner/repo",
        manifest=dict(INCOMPLETE_MANIFEST),
    )
    plugin = repository.create_plugin(db_session, data)
    result = analyze(plugin.manifest)
    analysis = repository.create_analysis(db_session, plugin.id, result)

    fresh = SessionLocal()
    try:
        retrieved = repository.get_analysis(fresh, analysis.id)
        assert retrieved is not None
        assert len(retrieved.findings) == len(result.findings)
        for orig, persisted in zip(result.findings, retrieved.findings):
            assert orig.check_id == persisted.check_id
            assert orig.severity.value == persisted.severity
            assert isinstance(persisted.evidence, dict)
    finally:
        fresh.close()


def test_audit_log_recorded_on_create(db_session):
    """log_event writes a searchable audit row."""
    data = PluginCreate(
        name="audit-test",
        description="Plugin for audit logging verification.",
        source="owner/repo",
        manifest={"name": "audit-test", "source": "owner/repo"},
    )
    plugin = repository.create_plugin(db_session, data)
    log_event(db_session, "create", "plugin", plugin.id, {"name": plugin.name})

    fresh = SessionLocal()
    try:
        entries = fresh.query(AuditLog).filter(AuditLog.action == "create").all()
        assert len(entries) == 1
        assert entries[0].entity_type == "plugin"
        assert entries[0].entity_id == plugin.id
    finally:
        fresh.close()