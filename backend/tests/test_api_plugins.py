"""API tests for plugin CRUD — crosses the real ASGI HTTP boundary."""

from __future__ import annotations

from sample_data import CLEAN_MANIFEST, LSP_MISSING_CONFIG, plugin_create_payload


def test_create_and_get_plugin(client):
    payload = plugin_create_payload(CLEAN_MANIFEST)
    resp = client.post("/api/v1/plugins", json=payload)
    assert resp.status_code == 201
    plugin = resp.json()
    plugin_id = plugin["id"]

    resp2 = client.get(f"/api/v1/plugins/{plugin_id}")
    assert resp2.status_code == 200
    got = resp2.json()
    assert got["name"] == payload["name"]
    assert got["source"] == payload["source"]
    assert got["plugin_type"] == "lsp"


def test_create_duplicate_conflict(client):
    payload = plugin_create_payload(CLEAN_MANIFEST)
    first = client.post("/api/v1/plugins", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/plugins", json=payload)
    assert second.status_code == 409


def test_list_plugins_pagination(client):
    for manifest in (CLEAN_MANIFEST, LSP_MISSING_CONFIG):
        client.post("/api/v1/plugins", json=plugin_create_payload(manifest))

    resp = client.get("/api/v1/plugins", params={"page": 1, "per_page": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["per_page"] == 1
    assert len(data["items"]) == 1


def test_search_filters_by_name(client):
    client.post("/api/v1/plugins", json=plugin_create_payload(CLEAN_MANIFEST))
    client.post("/api/v1/plugins", json=plugin_create_payload(LSP_MISSING_CONFIG))

    resp = client.get("/api/v1/plugins", params={"search": "typescript"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "typescript-lsp"


def test_update_plugin(client):
    payload = plugin_create_payload(CLEAN_MANIFEST)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    upd = client.put(
        f"/api/v1/plugins/{plugin_id}",
        json={"description": "Updated description for the plugin."},
    )
    assert upd.status_code == 200
    assert upd.json()["description"] == "Updated description for the plugin."


def test_delete_plugin(client):
    payload = plugin_create_payload(CLEAN_MANIFEST)
    resp = client.post("/api/v1/plugins", json=payload)
    plugin_id = resp.json()["id"]

    del_resp = client.delete(f"/api/v1/plugins/{plugin_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/v1/plugins/{plugin_id}")
    assert get_resp.status_code == 404


def test_get_nonexistent_plugin(client):
    resp = client.get("/api/v1/plugins/99999")
    assert resp.status_code == 404