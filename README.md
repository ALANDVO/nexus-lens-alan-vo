# Nexus Lens: Claude Code Plugin Registry · Alan Vo | AI & Machine Learning

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


**Every Claude Code plugin ships a manifest (`marketplace.json`, `.lsp.json`,
`plugin.json`). When those manifests are malformed, missing LSP configs, or
accidentally embed credentials, every user who installs the plugin gets a
broken or unsafe experience.** Nexus Lens provides a deterministic conformance
analysis engine that statically evaluates plugin manifests and assigns a
reproducible quality score, catching the same classes of failure reported
against the official marketplace (missing LSP configs, schema-invalid sources,
leaked tokens).

The offline engine runs with **no LLM key** and **no network access**. An
opt-in advisory LLM layer (planned) will surface natural-language explanations
of each finding, grounded in actual records.

**Intended users:** Claude Code plugin authors who want to verify their plugin
before submission, and registry maintainers who need to audit incoming plugins.

---

## Architecture

```mermaid
graph LR
    A[Browser] -->|REST JSON| B[Frontend<br/>React + TypeScript + Vite]
    B -->|REST JSON| C[Backend<br/>FastAPI (Python)]
    C --> D[(SQLite<br/>Persistent)]
    C --> E[Conformance Engine<br/>Deterministic checks + score]
    E -.->|opt-in advisory| F[LLM Explanations<br/>Planned]
    C -.->|OIDC| G[Keycloak + SAML IdP<br/>Planned]
```

## Features

| Feature | Status |
|---|---|
| Plugin registry — register, list, search, filter, paginate | ✅ |
| Deterministic conformance engine — 6 checks + 0–100 quality score | ✅ |
| Findings with severity, evidence, and audit trail | ✅ |
| Analysis persistence and retrieval | ✅ |
| React dashboard with TypeScript API client | ✅ |
| CLI for reproducible analysis (`analyze-manifest`) | ✅ |
| OIDC Keycloak SSO + SAML identity brokering | 🚧 planned |
| Opt-in LLM advisory explanations | 🚧 planned |

### Conformance checks

| Check | Severity | What it detects |
|---|---|---|
| `source.format` | FAIL | `source` is not a valid `owner/repo` reference (issue #587) |
| `lsp.config_present` | WARN | `lspServers` declared without a `.lsp.json` (`lspConfig`) (issue #379) |
| `plugin.required_fields` | WARN | Missing `name`, `description`, or `source` |
| `plugin.description_quality` | WARN | Description too short or placeholder text |
| `plugin.type_consistency` | WARN | Type is `lsp` but no `lspServers` declared |
| `security.token_scan` | FAIL | Credential-shaped values found in any manifest string |

**Scoring:** starts at 100. Each FAIL subtracts 25, each WARN subtracts 10
(clamped to 0–100). Bands: `excellent` ≥ 90, `good` ≥ 70, `needs_review` ≥ 50,
`poor` < 50.

---

## AI/ML Evaluation

The conformance engine is a **deterministic static-analysis infrastructure** for
the AI/ML developer ecosystem — it evaluates the quality and safety of plugins
that extend AI coding agents. No LLM is required for the core engine; the LLM
layer (when implemented) provides opt-in, labeled advisory explanations of
findings.

### Reproducible command

```bash
PYTHONPATH=backend .venv/bin/python -m app.cli analyze-manifest backend/sample-manifest.json
```

### Data provenance

`backend/sample-manifest.json` is derived from the public issue #379
("All LSP plugins missing `.lsp.json`"). It represents the **rust-analyzer LSP
plugin** as it would appear in a `marketplace.json` entry: valid source,
substantive description, LSP servers declared, but **no `.lsp.json` config
field** — exactly the gap reported by users.

### Baseline

The engine runs all six checks in a fixed order and aggregates the result into a
weighted score. The algorithm is fully deterministic: the same manifest always
produces the same score, findings, and evidence.

### Measured result (sample-manifest.json)

```
score:  90
band:   excellent
findings:
  - lsp.config_present  WARN
    "LSP servers declared in marketplace.json but no .lsp.json config (lspConfig) present."
    evidence: {"lsp_servers": ["rust"], "missing_field": "lspConfig"}
```

**One WARN** → score 100 − 10 = **90**, band `excellent`. The engine correctly
identifies the missing `.lsp.json` config that issue #379 describes.

### Failure cases

| Manifest defect | Check triggered | Severity | Score impact |
|---|---|---|---|
| `source: "not-a-valid-ref"` | `source.format` | FAIL | −25 |
| Missing `.lsp.json` for LSP plugin | `lsp.config_present` | WARN | −10 |
| Empty `name` / `description` / `source` | `plugin.*` | WARN each | −10 each |
| Credential-shaped value in any field | `security.token_scan` | FAIL | −25 |
| `type=invalid` | `source.format` + `plugin.source` | FAIL+WARN | −35 |

---

## Installation & run

### Backend

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt

# Run (default port 8000)
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev       # → http://localhost:5173 (proxies /api to backend)
```

### Docker (full stack with Keycloak)

```bash
docker compose up --build
# Backend:  http://127.0.0.1:8000
# Frontend: http://127.0.0.1:5173
# Keycloak: http://127.0.0.1:8081
```

### Local demo mode

Set `APP_ENV=demo` and bind to `127.0.0.1`. The app **refuses to start** in demo
mode if the host is not localhost, preventing accidental public exposure:

```bash
APP_ENV=demo APP_HOST=127.0.0.1 uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## Testing

### Backend

```bash
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests -v
```

Covers: conformance engine (check logic, scoring, edge cases), API workflows
(create/read/analyze), persistence, audit logging.

### Frontend

```bash
cd frontend
npm run typecheck
npm test
npm run build
```

Covers: API client request construction, component rendering (severity badges,
form validation), and dashboard data flow.

---

## API endpoint reference

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/api/v1/plugins` | List plugins (page, per_page, search, type, min_score, max_score) |
| POST | `/api/v1/plugins` | Register a new plugin |
| GET | `/api/v1/plugins/{id}` | Get plugin detail |
| PUT | `/api/v1/plugins/{id}` | Update plugin |
| DELETE | `/api/v1/plugins/{id}` | Delete plugin |
| POST | `/api/v1/plugins/{id}/analyze` | Run conformance analysis |
| GET | `/api/v1/plugins/analyses/{id}` | Retrieve an analysis with findings |
| GET | `/api/v1/plugins/{id}/analyses` | List analyses for a plugin |

---

## Provider configuration

The LLM advisory layer is **planned** and not yet implemented. No LLM calls are
made by the current build. When enabled, these are the configurable variables
(loaded from `.env`, never committed):

| Variable | Required | Description | Default |
|---|---|---|---|
| `LLM_API_KEY` | No (planned) | LLM API key — server-side only | (empty) |
| `LLM_PROVIDER` | No | Provider: `openai-compatible`, `anthropic`, `gemini`, `ollama` | (none) |
| `LLM_MODEL` | No | Model identifier | (provider default) |
| `LLM_BASE_URL` | No | Custom endpoint URL (OpenAI-compatible) | (provider default) |

**Security:** keys are never logged, never exposed to the frontend, and bounded
timeouts apply. Provider errors are returned as redacted messages — never
fabricated successes.

---

## SSO / SAML setup

Authentication is a **planned** milestone. The intended architecture is
backend-managed OpenID Connect authorization-code login through Keycloak
(state + nonce + PKCE) with HttpOnly SameSite cookies and CSRF protection on
writes. Keycloak also supports upstream SAML identity providers through identity
brokering.

The realm definition is pre-generated at
`backend/app/core/auth/keycloak/real.json`:

- **OIDC client** (`nexus-lens-frontend`) with PKCE `S256` challenge method
- **Roles** — `viewer` (read-only), `analyst` (manage plugins + analyses),
  `admin` (full access)
- **SAML identity provider** broker (`saml-broker`) with configurable upstream
  `singleSignOnService` and `singleLogoutService` URLs

To enrol an upstream SAML IdP:

1. Import `real.json` into Keycloak (`/opt/keycloak/data/import/real.json`)
2. Update the `identityProviders` entry with your IdP’s SSO/logout endpoints
3. Map IdP user attributes to Keycloak user properties in the broker configuration

Docker compose starts Keycloak on `127.0.0.1:8081` (import volume mounted
read-only).

---

## Security limitations

- **Auth is not yet enforced.** The API is open in this checkpoint. OIDC/Keycloak
  SSO is a planned milestone documented above.
- **SQLite file storage** is suitable for local development. Production
  deployments should use PostgreSQL behind a reverse proxy.
- **No rate limiting** is configured yet.
- The deterministic engine does **not** execute LSP servers or plugin code — it
  only inspects manifest data. Full LSP server invocation is out of scope.

---

## License

MIT © Alan Vo <alanvo@gmail.com>