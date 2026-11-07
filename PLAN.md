# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

export-workflow

## Roadmap

### conformance-engine — Plugin conformance analysis engine

Status: done

Acceptance:
- Register a plugin with manifest data (name, description, source, plugin config)
- Run deterministic conformance analysis producing findings and a 0-100 quality score
- View findings grouped by severity with evidence for each
- Persist plugins and analyses to SQLite; retrieve via typed API
- CLI command reproduces an analysis run on a sample manifest

Implementation: `backend/app/services/conformance.py`, `backend/app/core/security.py`, `backend/app/api/plugins.py`, `backend/app/api/analysis.py`

Tests: `backend/tests/test_conformance.py`, `backend/tests/test_api_plugins.py`, `backend/tests/test_api_analysis.py`, `backend/tests/test_persistence.py`

### plugin-registry — Plugin registry UI + search, filter, pagination

Status: done

Acceptance:
- React dashboard listing plugins with quality scores
- Search and filter plugins by name/type/score
- Plugin detail view with analysis findings

### export-workflow — Analysis export workflow

Status: done

Acceptance:
- Export a plugin or analysis report as JSON for review
- Frontend: "Export Plugin Report" button on plugin detail page
- Frontend: "Export" button for each analysis in the past analyses list

Implementation: `backend/app/api/analysis.py`, `frontend/src/api/client.ts`, `frontend/src/pages/PluginDetailPage.tsx`

Tests: `backend/tests/test_api_analysis.py`

### type-consistency — Enhanced plugin type consistency checks

Status: done

Acceptance:
- MCP plugin type requires mcpServers in config (WARN if missing)
- LSP plugin type requires lspServers in config (WARN if missing) - existing
- Reverse check: lspServers declared but plugin_type is not 'lsp' -> WARN
- Reverse check: mcpServers declared but plugin_type is not 'mcp' -> WARN
- Fully conformant MCP manifest with mcpServers scores 100

Implementation: `backend/app/services/conformance.py`, `backend/tests/test_conformance.py`

Tests: `backend/tests/test_conformance.py`

### auth-oidc — OIDC Keycloak SSO authentication & authorization

Status: planned

Acceptance:
- OIDC login callback
- role-based authorization on data endpoints
- logout

### llm-advisory — Opt-in LLM advisory explanations of findings

Status: planned

Acceptance:
- LLM explanation endpoint, clearly labeled advisory, redacted errors

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
