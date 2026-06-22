from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.enums import CropStageType, PestLifecycleStage, RiskLevel, SeverityLevel
from app.domain.shared.value_objects import GeoLocation, TimeWindow


class ValidationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class PredictionSnapshot(ValidationModel):
    prediction_id: str
    timestamp: datetime
    region: str
    crop_id: str
    pest_id: str
    predicted_stage: PestLifecycleStage
    predicted_risk: RiskLevel
    predicted_risk_score: float = Field(ge=0.0, le=1.0)
    predicted_outbreak_probability: float = Field(ge=0.0, le=1.0)
    expected_peak_window: Optional[TimeWindow] = None
    generated_recommendation_id: Optional[str] = None
    prediction_confidence: float = Field(ge=0.0, le=1.0)
    model_version: str = "mvp_v1"
    metadata: Dict[str, Any] = Field(default_factory=dict)


PredictionRecord = PredictionSnapshot


class FieldObservation(ValidationModel):
    observation_id: str
    timestamp: datetime
    location: GeoLocation
    crop_stage: CropStageType
    observed_pest_stage: Optional[PestLifecycleStage] = None
    observed_population_pressure: str = "unknown"
    observed_damage_level: str = "unknown"
    actual_outbreak: bool = False
    actual_outbreak_date: Optional[date] = None
    environmental_notes: List[str] = Field(default_factory=list)
    observer_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    observation_source: str = "manual_scouting"


class InterventionRecord(ValidationModel):
    intervention_id: str
    timestamp: datetime
    treatment_used: str
    target_pest: str
    target_stage: Optional[PestLifecycleStage] = None
    dosage: Optional[str] = None
    application_method: Optional[str] = None
    operational_conditions: Dict[str, Any] = Field(default_factory=dict)
    intervention_reason: List[str] = Field(default_factory=list)


class OutcomeRecord(ValidationModel):
    outcome_id: str
    timestamp: datetime
    observation_period_days: int = Field(ge=0)
    pest_population_change: str = "unknown"
    crop_damage_change: str = "unknown"
    outbreak_suppression: Optional[bool] = None
    side_effects: List[str] = Field(default_factory=list)
    treatment_effectiveness: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    recovery_indicators: List[str] = Field(default_factory=list)
    outcome_confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class ConfidenceAdjustment(ValidationModel):
    original_confidence: float = Field(ge=0.0, le=1.0)
    suggested_confidence: float = Field(ge=0.0, le=1.0)
    adjustment: float
    reasoning: List[str] = Field(default_factory=list)


class CalibrationSuggestion(ValidationModel):
    suggestion_id: str
    target: str
    suggested_adjustment: str
    reason: str
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    requires_human_review: bool = True


class LearningInsight(ValidationModel):
    insight_type: str
    message: str
    severity: SeverityLevel = SeverityLevel.MINOR
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    related_entities: List[str] = Field(default_factory=list)


class RegionalCalibrationProfile(ValidationModel):
    region: str
    pest_id: str
    calibration_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    suggested_gdd_adjustments: Dict[str, float] = Field(default_factory=dict)
    suggested_suitability_weight_adjustments: Dict[str, float] = Field(default_factory=dict)
    regional_anomalies: List[str] = Field(default_factory=list)


class ValidationResult(ValidationModel):
    validation_id: str
    prediction_id: str
    observation_id: str
    pest_id: str
    prediction_accuracy: float = Field(ge=0.0, le=1.0)
    risk_accuracy: float = Field(ge=0.0, le=1.0)
    stage_accuracy: float = Field(ge=0.0, le=1.0)
    outbreak_timing_accuracy: float = Field(ge=0.0, le=1.0)
    false_positive: bool
    false_negative: bool
    confidence_accuracy: float = Field(ge=0.0, le=1.0)
    calibration_gap: float = Field(ge=0.0, le=1.0)
    confidence_adjustment: ConfidenceAdjustment
    calibration_suggestions: List[CalibrationSuggestion] = Field(default_factory=list)
    learning_insights: List[LearningInsight] = Field(default_factory=list)
    validation_notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
