# app/domain/shared/entities/climate_state.py
from __future__ import annotations

from typing import List

from pydantic import Field

from app.domain.shared.base.aggregate_root import AggregateRoot
from app.domain.shared.enums import EnvironmentalEventType
from app.domain.shared.value_objects import (
    Anomaly,
    ClimateMetrics,
    DegreeDay,
    GeoLocation,
    HourlyClimateObservation,
)


class ClimateState(AggregateRoot):
    """
    Aggregate root representing environmental truth for the system.

    ClimateState is the canonical environmental state consumed by
    crop, pest, suitability, risk, and forecasting engines.

    It represents interpreted environmental intelligence,
    not raw weather ingestion.
    """

    location: GeoLocation

    current_conditions: HourlyClimateObservation

    degree_day: DegreeDay

    metrics: ClimateMetrics

    accumulated_gdd: float = Field(
        default=0.0,
        ge=0.0,
        description="Accumulated growing degree days.",
    )

    anomalies: List[Anomaly] = Field(
        default_factory=list,
        description="Detected abnormal environmental conditions.",
    )

    environmental_events: List[EnvironmentalEventType] = Field(
        default_factory=list,
        description="Detected environmental event classifications.",
    )

    reasoning: List[str] = Field(
        default_factory=list,
        description="Human-readable environmental reasoning trace.",
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in interpreted climate state.",
    )