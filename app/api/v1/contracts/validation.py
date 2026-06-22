from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from .base import ApiModel

class ValidationRequest(ApiModel):
    prediction_id: str
    pest_id: str
    crop_id: str
    region: str

    predicted_stage: str
    predicted_risk: str
    predicted_risk_score: float = Field(ge=0.0, le=1.0)
    predicted_outbreak_probability: float = Field(
        ge=0.0,
        le=1.0,
    )

    prediction_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    observation_timestamp: datetime
    observed_crop_stage: str
    observed_pest_stage: Optional[str] = None
    observed_population_pressure: str = "unknown"
    observed_damage_level: str = "unknown"
    actual_outbreak: bool = False
    observer_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )


class ValidationResponse(ApiModel):
    validation_id: str
    prediction_id: str
    pest_id: str
    prediction_accuracy: float
    risk_accuracy: float
    stage_accuracy: float
    outbreak_timing_accuracy: float
    false_positive: bool
    false_negative: bool
    confidence_accuracy: float
    calibration_gap: float
    validation_notes: List[str]