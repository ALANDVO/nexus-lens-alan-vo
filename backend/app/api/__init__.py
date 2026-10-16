from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

from .plugins import router as plugins_router  # noqa: E402
from .analysis import router as analysis_router  # noqa: E402
api_router.include_router(plugins_router)
api_router.include_router(analysis_router)