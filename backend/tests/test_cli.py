"""Tests for the Nexus Lens CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from sample_data import (
    CLEAN_MANIFEST,
    LSP_MISSING_CONFIG,
    manifest_with_synthetic_token,
)


def _run_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Run the CLI module and return the completed process."""
    return subprocess.run(
        [sys.executable, "-m", "app.cli"] + args,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )


def test_cli_analyze_manifest_clean():
    """CLI analyze-manifest on a clean manifest returns JSON with score 100."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(CLEAN_MANIFEST, f)
        f.flush()
        result = _run_cli(["analyze-manifest", f.name])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["score"] == 100
    assert data["band"] == "excellent"
    assert data["findings"] == []


def test_cli_analyze_manifest_lsp_missing_config():
    """CLI analyze-manifest on LSP manifest missing lspConfig returns WARN."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(LSP_MISSING_CONFIG, f)
        f.flush()
        result = _run_cli(["analyze-manifest", f.name])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["score"] == 90
    assert data["band"] == "excellent"
    assert len(data["findings"]) == 1
    assert data["findings"][0]["check_id"] == "lsp.config_present"
    assert data["findings"][0]["severity"] == "warn"
def test_cli_analyze_manifest_token_scan_fails():
    """CLI analyze-manifest on manifest with token returns FAIL."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(manifest_with_synthetic_token(), f)
        f.flush()
        result = _run_cli(["analyze-manifest", f.name])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["score"] == 65
    assert data["band"] == "needs_review"
    token_findings = [f for f in data["findings"] if f["check_id"] == "security.token_scan"]
    assert len(token_findings) == 1
    assert token_findings[0]["severity"] == "fail"
    # Also check type_consistency warn is present
    type_findings = [f for f in data["findings"] if f["check_id"] == "plugin.type_consistency"]
    assert len(type_findings) == 1
    assert type_findings[0]["severity"] == "warn"


def test_cli_analyze_manifest_file_not_found():
    """CLI analyze-manifest with non-existent file returns error code 2."""
    result = _run_cli(["analyze-manifest", "/nonexistent/manifest.json"])
    assert result.returncode == 2
    assert "error: file not found" in result.stderr


def test_cli_analyze_manifest_invalid_json():
    """CLI analyze-manifest with invalid JSON returns error code 2."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not valid json")
        f.flush()
        result = _run_cli(["analyze-manifest", f.name])
    assert result.returncode == 2
    assert "error: invalid JSON" in result.stderr


def test_cli_analyze_manifest_not_object():
    """CLI analyze-manifest with JSON array returns error code 2."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        f.flush()
        result = _run_cli(["analyze-manifest", f.name])
    assert result.returncode == 2
    assert "error: manifest must be a JSON object" in result.stderr


def test_cli_help():
    """CLI --help prints usage."""
    result = _run_cli(["--help"])
    assert result.returncode == 0
    assert "analyze-manifest" in result.stdout
    assert "Nexus Lens" in result.stdout


def test_cli_no_args():
    """CLI with no args prints help and returns error."""
    result = _run_cli([])
    assert result.returncode == 2
    assert "usage:" in result.stderr.lower() or "usage:" in result.stdout.lower()

