"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..core.database import get_session

# Primary DB-session dependency used by all routes.
DbSession = Annotated[Session, Depends(get_session)]