# app/domain/climate/contracts/weather_context.py
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.contracts import HourlyClimateObservation
from app.domain.shared.value_objects import GeoLocation


class WeatherContext(BaseModel):
    """
    Canonical weather input contract for biological climate computation.

    Infrastructure assembles this.
    Domain engines consume this.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        use_enum_values=True,
    )

    location: GeoLocation

    historical: list[HourlyClimateObservation] = Field(default_factory=list)

    current: HourlyClimateObservation | None = None

    forecast: list[HourlyClimateObservation] = Field(default_factory=list)

    source: str = "weather_context"

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(default_factory=dict)