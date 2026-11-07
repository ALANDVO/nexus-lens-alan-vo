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
def test_mcp_type_missing_mcpServers_warns():
    """MCP plugin type without mcpServers → WARN."""
    manifest = {
        "name": "mcp-server",
        "description": "MCP server plugin for Claude Code.",
        "source": "owner/repo",
        "plugin_type": "mcp",
        "config": {},
    }
    result = analyze(manifest)
    type_findings = [f for f in result.findings if f.check_id == "plugin.type_consistency"]
    assert len(type_findings) == 1
    assert type_findings[0].severity == Severity.WARN
    assert "mcpServers" in type_findings[0].message


def test_lspServers_declared_but_type_not_lsp_warns():
    """lspServers present but plugin_type is not 'lsp' → WARN."""
    manifest = {
        "name": "mixed-plugin",
        "description": "Plugin with lspServers but type is mcp.",
        "source": "owner/repo",
        "plugin_type": "mcp",
        "config": {
            "lspServers": {"python": {"command": "pyright", "args": ["--stdio"]}},
            "mcpServers": {"test": {"command": "echo"}},
        },
    }
    result = analyze(manifest)
    type_findings = [f for f in result.findings if f.check_id == "plugin.type_consistency"]
    assert len(type_findings) == 1
    assert type_findings[0].severity == Severity.WARN
    assert "lspServers" in type_findings[0].message


def test_mcpServers_declared_but_type_not_mcp_warns():
    """mcpServers present but plugin_type is not 'mcp' → WARN."""
    manifest = {
        "name": "mixed-plugin",
        "description": "Plugin with mcpServers but type is lsp.",
        "source": "owner/repo",
        "plugin_type": "lsp",
        "config": {
            "mcpServers": {"filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem"]}},
            "lspServers": {"python": {"command": "pyright", "args": ["--stdio"]}},
        },
    }
    result = analyze(manifest)
    type_findings = [f for f in result.findings if f.check_id == "plugin.type_consistency"]
    assert len(type_findings) == 1
    assert type_findings[0].severity == Severity.WARN
    assert "mcpServers" in type_findings[0].message


def test_mcpServers_declared_but_type_not_mcp_warns():
    """mcpServers present but plugin_type is not 'mcp' → WARN."""
    manifest = {
        "name": "mixed-plugin",
        "description": "Plugin with mcpServers but type is lsp.",
        "source": "owner/repo",
        "plugin_type": "lsp",
        "config": {
            "mcpServers": {"filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem"]}},
            "lspServers": {"python": {"command": "pyright", "args": ["--stdio"]}},
        },
    }
    result = analyze(manifest)
    type_findings = [f for f in result.findings if f.check_id == "plugin.type_consistency"]
    assert len(type_findings) == 1
    assert type_findings[0].severity == Severity.WARN
    assert "mcpServers" in type_findings[0].message


def test_clean_mcp_manifest_scores_excellent():
    """Fully conformant MCP manifest with mcpServers → score 100."""
    manifest = {
        "name": "filesystem-mcp",
        "description": "MCP server providing filesystem access for Claude Code.",
        "source": "owner/repo",
        "plugin_type": "mcp",
        "config": {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                }
            }
        },
    }
    result = analyze(manifest)
    assert result.score == 100
    assert result.band == "excellent"
    type_findings = [f for f in result.findings if f.check_id == "plugin.type_consistency"]
    assert type_findings == []


def test_clean_lsp_with_lspServers_but_no_lspConfig_still_warns():
    """LSP plugin with lspServers but missing lspConfig → WARN from lsp.config_present, not type_consistency."""
    manifest = {
        "name": "python-lsp",
        "description": "Python language server plugin for Claude Code with full features.",
        "source": "owner/repo",
        "plugin_type": "lsp",
        "config": {
            "lspServers": {"python": {"command": "pyright", "args": ["--stdio"]}},
        },
    }
    result = analyze(manifest)
    type_findings = [f for f in result.findings if f.check_id == "plugin.type_consistency"]
    assert type_findings == []
    lsp_findings = [f for f in result.findings if f.check_id == "lsp.config_present"]
    assert len(lsp_findings) == 1
    assert lsp_findings[0].severity == Severity.WARN