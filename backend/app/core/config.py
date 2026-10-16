"""Application configuration (operator-controlled, no hardcoded secrets)."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./nexus_lens.db"

    # LLM adapter (opt-in advisory; no default endpoint)
    llm_api_key: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None

    # Keycloak (planned SSO)
    keycloak_url: str | None = None
    keycloak_realm: str | None = None
    keycloak_client_id: str | None = None
    keycloak_client_secret: str | None = None

    @property
    def is_demo_mode(self) -> bool:
        return self.app_env == "demo"

    @property
    def demo_allowed(self) -> bool:
        # Demo binds localhost only and refuses to start in production.
        return self.is_demo_mode and self.app_host in ("127.0.0.1", "localhost")

    @property
    def version(self) -> str:
        # Check cwd (Docker: /app, dev: repo root) then fallback to repo-root
        # relative resolution (dev layout: backend/app/core → root).
        candidates = [
            Path.cwd() / "VERSION",
            Path(__file__).resolve().parents[3] / "VERSION",
        ]
        for path in candidates:
            if path.is_file():
                return path.read_text().strip()
        return "0.0.0"


settings = Settings()