from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class SuitabilityScore(ValueObject):
    """
    Environmental biological favorability scoring container.

    Represents decomposed suitability evaluation output
    for downstream risk and recommendation logic.
    """

    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Final normalized suitability score.",
    )

    temperature_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Temperature suitability component.",
    )

    humidity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Humidity suitability component.",
    )

    rainfall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Rainfall suitability component.",
    )

    crop_stage_modifier: float = Field(
        default=1.0,
        ge=0.0,
        description="Host-stage biological opportunity modifier.",
    )

    stability_modifier: float = Field(
        default=1.0,
        ge=0.0,
        description="Environmental persistence modifier.",
    )