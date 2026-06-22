# app/infrastructure/storage/db/session.py
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.infrastructure.storage.db.base import Base


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    Base.metadata.drop_all(bind=engine)