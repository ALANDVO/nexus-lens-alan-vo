# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to Nexus Lens are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/) and the version follows
[SemVer](https://semver.org/).

## [1.0.0] — 2026-10-16

### Added

**Backend (FastAPI + SQLAlchemy + SQLite)**
- Plugin registry: create, read, update, delete, list with search, filtering
  by type/score, and pagination
- Deterministic conformance analysis engine with six checks: source format,
  LSP config presence, required fields, description quality, type consistency,
  and credential token scanning
- Quality score (0–100) with four bands: excellent, good, needs_review, poor
- Structured findings with severity, message, and evidence
- Analysis persistence with eager-loaded findings via `selectinload`
- Audit log for all mutations (create, update, delete, analyze)
- CLI command `analyze-manifest` for reproducible engine runs
- Health-check endpoint (`/health`)
- CORS middleware configured for localhost:5173

**Frontend (React + TypeScript + Vite)**
- Responsive dashboard listing plugins with quality-score badges
- Plugin registration form with real-time validation and manifest auto-generation
- Plugin detail page with "Run Analysis" workflow and findings view
- Analysis history with per-item drill-in
- Typed API client (`src/api/client.ts`) derived from actual backend routes
- Loading, error, and empty states throughout

**Packaging**
- Backend Dockerfile (Python 3.12-slim, non-root user, healthcheck)
- Frontend Dockerfile (multi-stage, non-root nginx on port 8080, SPA fallback)
- `compose.yaml` with backend, frontend, and Keycloak services + persistent volumes
- CI workflow: backend tests (pytest), frontend tests (vitest) + typecheck + build,
  Docker builds via `docker/setup-buildx-action`
- `.env.example` with blank credentials
- Keycloak realm export (`real.json`) with OIDC client, roles, and SAML IdP broker
- Demo mode with localhost-only binding guard

**Tests**
- 27 backend tests (engine, API, persistence, audit)
- 11 frontend tests (client, components, pages)

### Added — 2026-10-26 (export-workflow checkpoint)

**Backend (FastAPI)**
- JSON export endpoints for analysis reports and plugin reports
  - `GET /api/v1/plugins/{plugin_id}/export` — exports plugin with latest analysis
  - `GET /api/v1/plugins/analyses/{analysis_id}/export` — exports full analysis report
  - Both return `application/json` with `Content-Disposition: attachment` for download
- 5 new tests covering export functionality and 404 error cases

### Planned (next milestones)

- OIDC Keycloak SSO login (state + nonce + PKCE) with role-based authorization
- Opt-in LLM advisory explanations of findings (OpenAI/Anthropic/Gemini/Ollama adapters)
- Advanced search and filtering UI
