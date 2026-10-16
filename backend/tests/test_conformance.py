"""Unit tests for the deterministic conformance engine."""

from __future__ import annotations

from app.services.conformance import (
    AnalysisResult,
    Finding,
    Severity,
    analyze,
    compute_score,
    score_band,
)
from sample_data import (
    BAD_SOURCE_MANIFEST,
    CLEAN_MANIFEST,
    INCOMPLETE_MANIFEST,
    LSP_MISSING_CONFIG,
    manifest_with_synthetic_token,
)


# --- Score bands and clamping ---

def test_score_clamping_to_zero():
    findings = [Finding("x", Severity.FAIL, "m", {}) for _ in range(5)]
    assert compute_score(findings) == 0


def test_score_no_findings_is_hundred():
    assert compute_score([]) == 100


def test_score_band_thresholds():
    assert score_band(100) == "excellent"
    assert score_band(90) == "excellent"
    assert score_band(89) == "good"
    assert score_band(70) == "good"
    assert score_band(69) == "needs_review"
    assert score_band(50) == "needs_review"
    assert score_band(49) == "poor"
    assert score_band(0) == "poor"


# --- Individual checks ---

def test_clean_manifest_scores_excellent():
    result = analyze(CLEAN_MANIFEST)
    assert result.score == 100
    assert result.band == "excellent"
    assert result.findings == []
    assert len(result.checks_run) == 6


def test_invalid_source_format_fails():
    result = analyze(BAD_SOURCE_MANIFEST)
    source_findings = [f for f in result.findings if f.check_id == "source.format"]
    assert len(source_findings) == 1
    assert source_findings[0].severity == Severity.FAIL
    assert "Invalid input" in source_findings[0].message or "not a valid" in source_findings[0].message


def test_missing_lsp_config_warns():
    """LSP server declared but no .lsp.json → WARN (issue claude-plugins-official#379)."""
    result = analyze(LSP_MISSING_CONFIG)
    lsp_findings = [f for f in result.findings if f.check_id == "lsp.config_present"]
    assert len(lsp_findings) == 1
    assert lsp_findings[0].severity == Severity.WARN
    assert "lspConfig" in lsp_findings[0].evidence["missing_field"]


def test_lsp_config_present_is_clean():
    result = analyze(CLEAN_MANIFEST)
    lsp_findings = [f for f in result.findings if f.check_id == "lsp.config_present"]
    assert lsp_findings == []


def test_short_description_warns():
    result = analyze(INCOMPLETE_MANIFEST)
    desc_findings = [f for f in result.findings if f.check_id == "plugin.description_quality"]
    assert len(desc_findings) >= 1
    assert desc_findings[0].severity == Severity.WARN


def test_missing_required_fields_warn():
    result = analyze(INCOMPLETE_MANIFEST)
    plugin_findings = {f.check_id for f in result.findings if f.check_id.startswith("plugin.")}
    # name is empty → required field WARN
    assert "plugin.name" in plugin_findings
    # description is "x" (non-empty but too short → description_quality WARN)
    assert "plugin.description_quality" in plugin_findings
    # source is empty → required field WARN
    assert "plugin.source" in plugin_findings

def test_missing_required_source_also_fails_format():
    result = analyze(INCOMPLETE_MANIFEST)
    source_findings = [f for f in result.findings if f.check_id == "source.format"]
    assert len(source_findings) == 1
    assert source_findings[0].severity == Severity.FAIL


def test_token_scan_detects_credential():
    """A runtime-constructed synthetic token must be flagged as FAIL."""
    result = analyze(manifest_with_synthetic_token())
    token_findings = [f for f in result.findings if f.check_id == "security.token_scan"]
    assert len(token_findings) >= 1
    assert token_findings[0].severity == Severity.FAIL
    assert "github_pat" in token_findings[0].evidence["patterns"] or "github_short" in token_findings[0].evidence["patterns"]