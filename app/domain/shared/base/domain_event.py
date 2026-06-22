from datetime import datetime, timezone
from typing import Any

from pydantic import Field

from app.domain.shared.base.domain_model import DomainModel


class DomainEvent(DomainModel):
    """Framework-free domain event contract."""

    event_id: str
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
