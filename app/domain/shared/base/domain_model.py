# app/domain/shared/base/domain_model.py
from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """Immutable Pydantic base for shared scientific primitives."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        use_enum_values=True,
    )
