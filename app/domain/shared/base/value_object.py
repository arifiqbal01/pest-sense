
# app/domain/shared/base/value_object.py
from app.domain.shared.base.domain_model import DomainModel


class ValueObject(DomainModel):
    """Marker base for immutable value objects."""
