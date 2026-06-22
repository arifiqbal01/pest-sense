from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class DegreeDay(ValueObject):
    """
    Represents normalized thermal accumulation used for
    biological development modeling.

    Degree-day interpretation is strategy-dependent
    (simple average, hourly integration, single sine, etc.),
    but this value object remains calculation-method agnostic.
    """

    daily_value: float = Field(
        ge=0.0,
        description="Thermal units accumulated for the current period.",
    )

    accumulated_value: float = Field(
        ge=0.0,
        description="Cumulative thermal units over time.",
    )

    calculation_method: str = Field(
        default="simple_average",
        min_length=1,
        description="Degree-day calculation strategy identifier.",
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in thermal accumulation accuracy.",
    )