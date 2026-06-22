from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject
from app.domain.shared.enums import SeverityLevel


class ExplanationFragment(ValueObject):
    """
    Structured explainability fragment for transparent domain reasoning.

    Used across climate, crop, pest, suitability, risk,
    recommendation, and validation modules.
    """

    source_module: str = Field(
        min_length=1,
        description="Domain module that generated this explanation.",
    )

    message: str = Field(
        min_length=1,
        description="Human-readable reasoning statement.",
    )

    severity: SeverityLevel = Field(
        default=SeverityLevel.MINOR,
        description="Importance level of this explanation fragment.",
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this reasoning fragment.",
    )

    related_entities: list[str] = Field(
        default_factory=list,
        description="Referenced domain entities (pests, crops, events, etc.).",
    )