from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject
from app.domain.shared.enums import ConfidenceLevel
from app.domain.shared.utils.scoring import clamp_score


class ConfidenceScore(ValueObject):
    """
    Standardized confidence representation for scientific
    and decision intelligence outputs.
    """

    value: float = Field(
        ge=0.0,
        le=1.0,
    )

    category: ConfidenceLevel

    contributing_factors: list[str] = Field(
        default_factory=list,
    )

    @classmethod
    def from_value(
        cls,
        value: float,
        factors: list[str] | None = None,
    ) -> "ConfidenceScore":
        bounded = clamp_score(value)

        if bounded < 0.20:
            category = ConfidenceLevel.VERY_LOW
        elif bounded < 0.40:
            category = ConfidenceLevel.LOW
        elif bounded < 0.70:
            category = ConfidenceLevel.MODERATE
        elif bounded < 0.85:
            category = ConfidenceLevel.MODERATE_HIGH
        elif bounded < 0.95:
            category = ConfidenceLevel.HIGH
        else:
            category = ConfidenceLevel.VERY_HIGH

        return cls(
            value=bounded,
            category=category,
            contributing_factors=factors or [],
        )