# app/domain/shared/base/aggregate_root.py
from app.domain.shared.base.entity import Entity


class AggregateRoot(Entity):
    """Marker base for aggregate roots."""
