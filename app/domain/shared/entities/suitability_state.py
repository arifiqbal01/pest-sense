# app/domain/shared/entities/suitability_state.py
from __future__ import annotations

from typing import List

from pydantic import Field

from app.domain.shared.base.aggregate_root import AggregateRoot
from app.domain.shared.value_objects import (
    ConfidenceScore,
    EnvironmentalStability,
    SuitabilityScore,
)


class SuitabilityState(AggregateRoot):
    """
    Aggregate root representing environmental biological favorability
    for a specific pest.

    Suitability is environmental opportunity, not actual abundance
    or outbreak risk.
    """

    pest_name: str = Field(
        min_length=1,
        description="Canonical pest identifier.",
    )

    score: SuitabilityScore

    environmental_stability: EnvironmentalStability = Field(
        default_factory=EnvironmentalStability,
    )

    contributing_factors: List[str] = Field(
        default_factory=list,
        description="Drivers increasing suitability.",
    )

    limiting_factors: List[str] = Field(
        default_factory=list,
        description="Drivers suppressing suitability.",
    )

    evaluation_method: str = Field(
        default="weighted_suitability_v1",
        min_length=1,
    )

    confidence: ConfidenceScore

    @property
    def overall_suitability(self) -> float:
        return self.score.overall_score