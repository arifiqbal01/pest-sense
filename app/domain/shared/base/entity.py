# app/domain/shared/base/entity.py
from pydantic import Field

from app.domain.shared.base.domain_model import DomainModel


class Entity(DomainModel):
    """Base entity with identity-based domain semantics."""

    id: str = Field(min_length=1)
