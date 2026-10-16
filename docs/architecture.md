# Architecture

## Overview

Nexus Lens is a full-stack application that registers Claude Code plugin
manifests and runs a deterministic static-analysis engine over them to produce
quality and safety scores. The engine is the core domain surface; everything
else (persistence, API, UI) exists to support the analysis workflow.

## Component map

```
frontend/          React + TypeScript + Vite (SPA, dev on :5173)
  ├─ src/api/      Typed fetch client ↔ backend REST routes
  ├─ src/components/  SeverityBadge, ScoreBadge, PluginList, PluginForm, AnalysisView
  ├─ src/pages/    Dashboard, NewPlugin, PluginDetail
backend/
  ├─ app/main.py   FastAPI factory, CORS, demo-mode guard
  ├─ app/core/     config, database, security (token patterns)
  ├─ app/models/   Plugin, AnalysisResult, Finding, AuditLog (SQLAlchemy ORM)
  ├─ app/schemas/  Pydantic request/response models
  ├─ app/api/      health, plugins, analysis routers (prefix /api/v1)
  ├─ app/services/ conformance engine, repository, audit
  └─ tests/        pytest suite (27 tests)
```

## Data flow

1. **User** registers a plugin via the React form → POST `/api/v1/plugins`.
2. **Backend** stores the manifest in SQLite, returns the created `Plugin`.
3. **User** clicks “Run Analysis” → POST `/api/v1/plugins/{id}/analyze`.
4. **Engine** (`app.services.conformance`) inspects the manifest dict with six
   deterministic checks and returns an `AnalysisResult` (score + findings).
5. **Backend** persists the analysis + findings, updates the plugin’s
   `latest_score`/`latest_band`, returns the full result.
6. **Frontend** renders the score, band badge, and sorted findings.

## Conformance engine

The engine (`conformance.analyze`) is a pure function: `manifests → 
AnalysisResult`. Each check is an independent function returning `Finding`
objects. The score is a deterministic weighted sum:

```
score = max(0, min(100, 100 - 25 * num_fails - 10 * num_warns))
band  = "excellent"     if score >= 90
      | "good"          if score >= 70
      | "needs_review"  if score >= 50
      | "poor"          otherwise
```

No randomness, no network, no LLM — reproducible by design.

## Database

SQLite (file-based) via SQLAlchemy 2.0 (sync). Tables: `plugins`,
`analysis_results`, `findings`, `audit_log`. Foreign keys are enforced.
The `analysis_results`→`findings` and `plugins`→`analysis_results`
relationships use `selectinload` for eager loading.

## Deployment

- **Docker**: multi-stage builds; backend on `python:3.12-slim`, frontend on
  `nginx:1.27-alpine` (non-root, port 8080).
- **Compose**: backend + frontend + Keycloak, ports bound to `127.0.0.1`.
- **Auth**: OIDC through Keycloak (planned), SAML via identity brokering.
- **Demo mode**: `APP_ENV=demo` refuses to start unless bound to localhost.