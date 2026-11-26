# Changelog

## 1.7.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.6.1 — work-in-progress checkpoint

### Added
- OIDC Keycloak SSO: login callback with PKCE S256, state verification, error handling
- `/auth/login` route with PKCE code challenge generation
- `/auth/callback` route with error/code/state validation
- `/auth/logout` route redirect to Keycloak
- `/auth/me` endpoint returning user from session

### Changed
- Auth routes now read Keycloak settings from config module (.env)
- Improved error handling and validation in callback

## 1.6.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.1 — work-in-progress checkpoint

### Added
- OIDC Keycloak SSO authentication flow (login, callback, logout, me endpoint)

### Planned
- role-based authorization on data endpoints using Keycloak realms
- logout endpoint completion

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — initial release

Initial release of Nexus Lens plugin registry and conformance analyzer.

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
