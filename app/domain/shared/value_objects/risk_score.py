from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject
from app.domain.shared.enums import SeverityLevel


class RiskScore(ValueObject):
    """
    Normalized risk scoring container.

    Represents scientific/operational risk evaluation output.
    """

    value: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalized risk score.",
    )

    severity: SeverityLevel

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in risk evaluation.",
    )

    contributing_factors: list[str] = Field(
        default_factory=list,
    )