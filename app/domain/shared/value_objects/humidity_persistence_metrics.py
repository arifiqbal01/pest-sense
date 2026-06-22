from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class HumidityPersistenceMetrics(ValueObject):
    """
    Temporal humidity persistence descriptor.

    Critical for biological survival, reproduction,
    fungal pressure, and environmental persistence logic.
    """

    humid_hours_24h: int = Field(
        default=0,
        ge=0,
    )

    humid_hours_72h: int = Field(
        default=0,
        ge=0,
    )

    saturation_hours_24h: int = Field(
        default=0,
        ge=0,
    )

    saturation_hours_72h: int = Field(
        default=0,
        ge=0,
    )

    nighttime_humid_hours: int = Field(
        default=0,
        ge=0,
    )

    persistence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )