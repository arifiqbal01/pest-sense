from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.container import container
from app.infrastructure.storage.db.session import SessionLocal

router = APIRouter(
    tags=["system"],
)


@router.get("/")
def root() -> dict[str, str]:
    return {
        "name": container.settings.APP_NAME,
        "status": "running",
        "environment": container.settings.APP_ENV,
    }


@router.get("/health")
def health() -> dict[str, str]:
    db_status = "failed"

    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        db_status = "connected"

    except Exception:
        pass

    return {
        "status": (
            "healthy"
            if db_status == "connected"
            else "degraded"
        ),
        "database": db_status,
        "weather_provider": container.settings.WEATHER_PROVIDER,
    }