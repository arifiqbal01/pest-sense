from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class Rainfall(ValueObject):
    """
    Rainfall environmental value object.

    Represents precipitation amount plus optional
    interpreted event characteristics.
    """

    amount_mm: float = Field(
        default=0.0,
        ge=0.0,
        description="Rainfall accumulation in millimeters.",
    )

    intensity: str = Field(
        default="none",
        min_length=1,
        description="Qualitative rainfall intensity classification.",
    )

    duration_hours: float | None = Field(
        default=None,
        ge=0.0,
        description="Rainfall event duration in hours.",
    )