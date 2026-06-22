# app/domain/shared/entities/pest_state.py
from __future__ import annotations

from typing import List

from pydantic import Field

from app.domain.shared.base.aggregate_root import AggregateRoot
from app.domain.shared.enums import (
    BiologicalEventType,
    OutbreakStatus,
    PestLifecycleStage,
)
from app.domain.shared.value_objects import (
    ConfidenceScore,
    PopulationPressure,
    Trend,
)


class PestState(AggregateRoot):
    """
    Aggregate root representing biological pest state.

    PestState is the canonical pest biology truth consumed by
    suitability, risk, recommendation, forecasting, and validation
    engines.

    This models pest biology, not economic decision logic.
    """

    pest_name: str = Field(
        min_length=1,
        description="Canonical pest identifier.",
    )

    scientific_name: str | None = Field(
        default=None,
        description="Optional scientific taxonomic name.",
    )

    current_stage: PestLifecycleStage

    accumulated_gdd: float = Field(
        default=0.0,
        ge=0.0,
        description="Accumulated pest thermal development units.",
    )

    stage_progression_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Normalized lifecycle stage progression.",
    )

    population_pressure: PopulationPressure

    outbreak_likelihood: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Estimated outbreak progression likelihood.",
    )

    outbreak_status: OutbreakStatus

    trend_state: Trend

    biological_flags: List[BiologicalEventType] = Field(
        default_factory=list,
        description="Biological state flags and special conditions.",
    )

    reasoning: List[str] = Field(
        default_factory=list,
        description="Human-readable biological reasoning trace.",
    )

    confidence: ConfidenceScore