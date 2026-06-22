# app/domain/shared/entities/recommendation.py
from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from app.domain.shared.base.aggregate_root import AggregateRoot
from app.domain.shared.enums import (
    InterventionType,
    PestLifecycleStage,
    RecommendationStatus,
    UrgencyLevel,
)
from app.domain.shared.value_objects import (
    ConfidenceScore,
    TimeWindow,
)


class Recommendation(AggregateRoot):
    """
    Aggregate root representing actionable agricultural decision intelligence.

    Recommendation translates biological and operational intelligence
    into intervention guidance.

    It does not execute interventions.
    """

    recommended_action: str = Field(
        min_length=1,
        description="Primary recommended intervention/action.",
    )

    intervention_type: InterventionType

    target_pest: str = Field(
        min_length=1,
        description="Canonical pest target identifier.",
    )

    target_stage: PestLifecycleStage

    urgency: UrgencyLevel

    timing_window: Optional[TimeWindow] = Field(
        default=None,
        description="Operational execution window.",
    )

    expected_effectiveness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Estimated intervention effectiveness.",
    )

    expected_risk_reduction: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Estimated operational risk reduction.",
    )

    status: RecommendationStatus = RecommendationStatus.GENERATED

    operational_notes: List[str] = Field(
        default_factory=list,
        description="Execution constraints, warnings, or notes.",
    )

    reasoning: List[str] = Field(
        default_factory=list,
        description="Human-readable recommendation reasoning.",
    )

    alternative_options: List[str] = Field(
        default_factory=list,
        description="Fallback intervention options.",
    )

    confidence: ConfidenceScore