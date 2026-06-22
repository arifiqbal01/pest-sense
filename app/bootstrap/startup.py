from __future__ import annotations

from app.core.container import container
from app.infrastructure.storage.db.session import create_all_tables


def startup():
    create_all_tables()
    return container