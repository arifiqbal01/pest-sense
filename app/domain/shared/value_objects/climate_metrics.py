from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class ClimateMetrics(ValueObject):
    """
    Derived temporal environmental metrics.

    Shared environmental truth consumed by:
    climate, suitability, risk, forecast, validation.
    """

    temperature_mean_24h: float
    temperature_mean_72h: float

    humidity_mean_24h: float = Field(
        ge=0.0,
        le=100.0,
    )

    humidity_mean_72h: float = Field(
        ge=0.0,
        le=100.0,
    )

    rainfall_24h: float = Field(
        default=0.0,
        ge=0.0,
    )

    rainfall_72h: float = Field(
        default=0.0,
        ge=0.0,
    )

    rainfall_7d: float = Field(
        default=0.0,
        ge=0.0,
    )

    humid_hours_24h: int = Field(
        default=0,
        ge=0,
    )

    humid_hours_72h: int = Field(
        default=0,
        ge=0,
    )

    heat_stress_hours_24h: int = Field(
        default=0,
        ge=0,
    )

    heat_stress_hours_72h: int = Field(
        default=0,
        ge=0,
    )

    cold_stress_hours_24h: int = Field(
        default=0,
        ge=0,
    )

    cold_stress_hours_72h: int = Field(
        default=0,
        ge=0,
    )