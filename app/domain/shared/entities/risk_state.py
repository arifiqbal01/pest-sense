# app/domain/shared/entities/risk_state.py
from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from app.domain.shared.base.aggregate_root import AggregateRoot
from app.domain.shared.enums import (
    RiskLevel,
    SeverityLevel,
    UrgencyLevel,
)
from app.domain.shared.value_objects import (
    ConfidenceScore,
    TimeWindow,
)


class RiskState(AggregateRoot):
    """
    Aggregate root representing operational agricultural risk
    for a pest in current context.

    Risk is contextual interpretation of biological, environmental,
    crop, and temporal pressures.
    """

    pest_name: str = Field(
        min_length=1,
        description="Canonical pest identifier.",
    )

    risk_level: RiskLevel

    risk_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalized aggregate risk score.",
    )

    urgency: UrgencyLevel

    severity: SeverityLevel

    outbreak_probability: float = Field(
        ge=0.0,
        le=1.0,
        description="Estimated outbreak escalation probability.",
    )

    expected_peak_window: Optional[TimeWindow] = Field(
        default=None,
        description="Estimated likely outbreak peak timing window.",
    )

    contributing_factors: List[str] = Field(
        default_factory=list,
        description="Risk amplifiers.",
    )

    limiting_factors: List[str] = Field(
        default_factory=list,
        description="Risk suppressors.",
    )

    reasoning: List[str] = Field(
        default_factory=list,
        description="Human-readable risk reasoning trace.",
    )

    evaluation_method: str = Field(
        default="weighted_risk_v1",
        min_length=1,
    )

    confidence: ConfidenceScore