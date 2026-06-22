from __future__ import annotations

from typing import Any

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class Metadata(ValueObject):
    """
    Generic provenance and confidence metadata.

    Shared across scientific domain objects.
    """

    source: str = "manual"

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    notes: list[str] = Field(
        default_factory=list,
    )

    extra: dict[str, Any] = Field(
        default_factory=dict,
    )