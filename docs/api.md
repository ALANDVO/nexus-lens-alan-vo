# API Reference

Base URL: `http://127.0.0.1:8000`

All endpoints return JSON. Errors use standard HTTP status codes with a
`{"detail": "..."}` body.

## Health

### `GET /health`

Health-check probe used by Docker healthchecks.

**Response 200**
```json
{"status": "ok", "time": "2026-10-16T12:00:00+00:00"}
```

## Plugins

### `GET /api/v1/plugins`

List plugins with pagination, search, and filtering.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number (≥1) |
| `per_page` | int | 20 | Items per page (1–100) |
| `search` | string | — | Match name/description/source (case-insensitive) |
| `type` | string | — | Filter by plugin type (`lsp`, `mcp`, `hook`, `other`) |
| `min_score` | int | — | Filter plugins with score ≥ value (0–100) |
| `max_score` | int | — | Filter plugins with score ≤ value (0–100) |

**Response 200**
```json
{
  "items": [{"id": 1, "name": "typescript-lsp", "description": "...", ...}],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### `POST /api/v1/plugins`

Register a new plugin.

**Body**
```json
{
  "name": "typescript-lsp",
  "description": "Language Server Protocol plugin for TypeScript.",
  "source": "anthropics/claude-plugins-official",
  "plugin_type": "lsp",
  "manifest": { "name": "...", "source": "...", "config": { ... } }
}
```

**Response 201** — the created plugin object.
**Response 409** — plugin name already registered.

### `GET /api/v1/plugins/{id}`

Retrieve a single plugin. **Response 200** / **404**.

### `PUT /api/v1/plugins/{id}`

Update plugin fields (partial). **Response 200** / **404**.

### `DELETE /api/v1/plugins/{id}`

Delete a plugin. **Response 204** / **404**.

## Analyses

### `POST /api/v1/plugins/{id}/analyze`

Run the deterministic conformance engine on the plugin's manifest.

**Response 200**
```json
{
  "id": 1,
  "plugin_id": 1,
  "score": 90,
  "band": "excellent",
  "checks_run": ["check_source_format", "check_lsp_config", ...],
  "findings": [
    {
      "check_id": "lsp.config_present",
      "severity": "warn",
      "message": "...",
      "evidence": {"lsp_servers": ["rust"], "missing_field": "lspConfig"}
    }
  ],
  "created_at": "2026-10-16T12:00:00"
}
```

### `GET /api/v1/plugins/analyses/{id}`

Retrieve a previously run analysis with all findings. **Response 200** / **404**.

### `GET /api/v1/plugins/{id}/analyses`

List all analyses for a plugin (summaries, no findings body).

**Response 200**
```json
[
  {"id": 2, "plugin_id": 1, "score": 90, "band": "excellent",
   "checks_run": [...], "created_at": "2026-10-16T12:00:00"}
]
```