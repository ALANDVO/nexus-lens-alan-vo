"""Nexus Lens — FastAPI application factory.

Usage:
    uvicorn app.main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .core.config import settings
from .core.database import init_db
from .api import api_router
from .api.health import router as health_router

_origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]


def get_cors_origins() -> list[str]:
    return list(_origins)


def create_app() -> FastAPI:
    """Application factory.

    Ensures the DB schema exists and mounts the v1 API router.
    Docker and local commands must use the same entry point
    (``uvicorn app.main:app``).
    """
    if settings.is_demo_mode and not settings.demo_allowed:
        raise RuntimeError(
            "Demo mode (APP_ENV=demo) refuses to start when not bound to "
            "127.0.0.1 or localhost."
        )

    init_db()

    app = FastAPI(
        title="Nexus Lens",
        description="Registry + conformance analyzer for Claude Code plugins.",
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/v1/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Root → API docs (dev convenience).
    @app.get("/")
    def root():
        return RedirectResponse(url="/docs")
    app.include_router(health_router)

    app.include_router(api_router)
    return app


app = create_app()