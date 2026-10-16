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

Status: planned

Acceptance:
- Export a plugin or analysis report as JSON for review

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

