from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class HourlyClimateObservation(ValueObject):
    """
    Atomic hourly environmental observation.

    Core primitive for:
    - hourly GDD
    - stress exposure
    - humidity persistence
    - anomaly detection
    - greenhouse telemetry
    """

    observed_at: datetime

    temperature_c: float

    humidity: float = Field(
        ge=0.0,
        le=100.0,
    )

    rainfall_mm: float = Field(
        default=0.0,
        ge=0.0,
    )

    wind_speed_kph: float | None = Field(
        default=None,
        ge=0.0,
    )

    pressure_msl: float | None = None

    cloud_cover_pct: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    solar_radiation_w_m2: float | None = Field(
        default=None,
        ge=0.0,
    )

    leaf_wetness: float | None = Field(
        default=None,
        ge=0.0,
    )