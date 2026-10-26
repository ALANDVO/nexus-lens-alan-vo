"""API tests for the conformance-analysis workflow (end-to-end)."""

from __future__ import annotations

from sample_data import (
    CLEAN_MANIFEST,
    LSP_MISSING_CONFIG,
    manifest_with_synthetic_token,
    plugin_create_payload,
)


def test_run_analysis_returns_score_and_findings(client):
    payload = plugin_create_payload(LSP_MISSING_CONFIG)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    resp2 = client.post(f"/api/v1/plugins/{plugin_id}/analyze")
    assert resp2.status_code == 200
    result = resp2.json()

    assert 0 <= result["score"] <= 100
    assert result["band"] in ("excellent", "good", "needs_review", "poor")
    assert len(result["checks_run"]) >= 1
    # LSP_MISSING_CONFIG → lsp.config_present WARN present
    lsp_findings = [f for f in result["findings"] if f["check_id"] == "lsp.config_present"]
    assert len(lsp_findings) == 1
    assert lsp_findings[0]["severity"] == "warn"


def test_clean_plugin_analysis_passes(client):
    payload = plugin_create_payload(CLEAN_MANIFEST)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    resp2 = client.post(f"/api/v1/plugins/{plugin_id}/analyze")
    result = resp2.json()
    assert result["score"] == 100
    assert result["band"] == "excellent"
    assert result["findings"] == []


def test_analysis_retrievable_by_id(client):
    payload = plugin_create_payload(manifest_with_synthetic_token())
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    resp2 = client.post(f"/api/v1/plugins/{plugin_id}/analyze")
    analysis_id = resp2.json()["id"]

    resp3 = client.get(f"/api/v1/plugins/analyses/{analysis_id}")
    assert resp3.status_code == 200
    analysis = resp3.json()
    assert analysis["id"] == analysis_id
    token_findings = [f for f in analysis["findings"] if f["check_id"] == "security.token_scan"]
    assert len(token_findings) >= 1
    assert token_findings[0]["severity"] == "fail"


def test_list_analyses_for_plugin(client):
    payload = plugin_create_payload(CLEAN_MANIFEST)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    client.post(f"/api/v1/plugins/{plugin_id}/analyze")
    client.post(f"/api/v1/plugins/{plugin_id}/analyze")

    resp2 = client.get(f"/api/v1/plugins/{plugin_id}/analyses")
    assert resp2.status_code == 200
    analyses = resp2.json()
    assert len(analyses) == 2
    assert analyses[0]["plugin_id"] == plugin_id


def test_analyze_nonexistent_plugin(client):
    resp = client.post("/api/v1/plugins/99999/analyze")
    assert resp.status_code == 404


def test_analysis_updates_plugin_latest_score(client):
    payload = plugin_create_payload(LSP_MISSING_CONFIG)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    resp2 = client.post(f"/api/v1/plugins/{plugin_id}/analyze")
    score = resp2.json()["score"]
    band = resp2.json()["band"]

    resp3 = client.get(f"/api/v1/plugins/{plugin_id}")
    plugin = resp3.json()
    assert plugin["latest_score"] == score
    assert plugin["latest_band"] == band

def test_export_analysis_report(client):
    """Test exporting an analysis report as JSON."""
    payload = plugin_create_payload(LSP_MISSING_CONFIG)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    resp2 = client.post(f"/api/v1/plugins/{plugin_id}/analyze")
    analysis_id = resp2.json()["id"]

    resp3 = client.get(f"/api/v1/plugins/analyses/{analysis_id}/export")
    assert resp3.status_code == 200
    assert resp3.headers["content-type"] == "application/json"
    assert "attachment" in resp3.headers["content-disposition"]
    assert f"analysis-{analysis_id}-report.json" in resp3.headers["content-disposition"]

    export_data = resp3.json()
    assert export_data["type"] == "analysis_report"
    assert export_data["plugin"]["id"] == plugin_id
    assert export_data["analysis"]["id"] == analysis_id
    assert "findings" in export_data["analysis"]
    assert export_data["analysis"]["score"] == resp2.json()["score"]
    assert export_data["analysis"]["band"] == resp2.json()["band"]


def test_export_plugin_report(client):
    """Test exporting a plugin with its latest analysis as JSON."""
    payload = plugin_create_payload(CLEAN_MANIFEST)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    client.post(f"/api/v1/plugins/{plugin_id}/analyze")

    resp2 = client.get(f"/api/v1/plugins/{plugin_id}/export")
    assert resp2.status_code == 200
    assert resp2.headers["content-type"] == "application/json"
    assert "attachment" in resp2.headers["content-disposition"]
    assert f"plugin-{plugin_id}-report.json" in resp2.headers["content-disposition"]

    export_data = resp2.json()
    assert export_data["type"] == "plugin_report"
    assert export_data["plugin"]["id"] == plugin_id
    assert export_data["latest_analysis"] is not None
    assert export_data["latest_analysis"]["id"] is not None
    assert "findings" in export_data["latest_analysis"]


def test_export_plugin_without_analysis(client):
    """Test exporting a plugin with no analyses."""
    payload = plugin_create_payload(CLEAN_MANIFEST)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    resp2 = client.get(f"/api/v1/plugins/{plugin_id}/export")
    assert resp2.status_code == 200
    export_data = resp2.json()
    assert export_data["type"] == "plugin_report"
    assert export_data["latest_analysis"] is None


def test_export_nonexistent_analysis(client):
    """Test exporting a non-existent analysis returns 404."""
    resp = client.get("/api/v1/plugins/analyses/99999/export")
    assert resp.status_code == 404


def test_export_nonexistent_plugin(client):
    """Test exporting a non-existent plugin returns 404."""
    resp = client.get("/api/v1/plugins/99999/export")
    assert resp.status_code == 404
