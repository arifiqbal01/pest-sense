# app/domain/shared/entities/crop_state.py
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import Field

from app.domain.shared.base.aggregate_root import AggregateRoot
from app.domain.shared.enums import CropStageType
from app.domain.shared.value_objects import ConfidenceScore


class CropState(AggregateRoot):
    """
    Aggregate root representing biological crop state.

    CropState is the canonical crop truth consumed by pest,
    suitability, risk, recommendation, forecasting, and validation
    engines.

    This models biological crop progression, not pest logic.
    """

    crop_type: str = Field(
        min_length=1,
        description="Crop identifier (e.g. cotton).",
    )

    cultivar: Optional[str] = Field(
        default=None,
        description="Optional cultivar/variety identifier.",
    )

    current_stage: CropStageType

    stage_started_at_day: int = Field(
        ge=0,
        description="Simulation-relative day when current stage began.",
    )

    stage_duration_days: int = Field(
        default=0,
        ge=0,
        description="Days spent in current stage.",
    )

    accumulated_development: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Normalized developmental completion.",
    )

    accumulated_gdd: float = Field(
        default=0.0,
        ge=0.0,
        description="Accumulated thermal development units.",
    )

    growth_velocity: float = Field(
        default=0.0,
        description="Relative crop developmental velocity.",
    )

    stress_state: Dict[str, float] = Field(
        default_factory=dict,
        description="Stress intensities by stress type.",
    )

    phenology: Dict[str, float | str] = Field(
        default_factory=dict,
        description="Phenology progression state.",
    )

    susceptibility_context: Dict[str, float] = Field(
        default_factory=dict,
        description="Pest susceptibility modifiers by pest.",
    )

    microclimate_modifiers: Dict[str, float] = Field(
        default_factory=dict,
        description="Crop-driven microclimate environmental modifiers.",
    )

    reasoning: List[str] = Field(
        default_factory=list,
        description="Human-readable crop reasoning trace.",
    )

    confidence: ConfidenceScore