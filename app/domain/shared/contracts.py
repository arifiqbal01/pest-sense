from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.enums import (
    BiologicalEventType,
    CropStageType,
    EnvironmentalEventType,
    InterventionType,
    OutbreakStatus,
    PestLifecycleStage,
    RecommendationStatus,
    RiskLevel,
    SeverityLevel,
    SimulationMode,
    TrendDirection,
    UrgencyLevel,
)
from app.domain.shared.value_objects import (
    DailyTemperature,
    DegreeDay,
    GeoLocation,
    PopulationPressure,
    SuitabilityScore,
    TimeWindow,
    Trend,
    Anomaly,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DomainState(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    id: str
    type: str
    version: str = "1.0"
    timestamp: datetime = Field(default_factory=utc_now)
    source: str = "pest_sense"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationContext(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    mode: SimulationMode = SimulationMode.CURRENT
    simulation_date: date = Field(default_factory=date.today)
    forecast_horizon_day: int = Field(default=0, ge=0)
    confidence_modifier: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "current"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClimateSnapshot(DomainState):
    type: str = "ClimateSnapshot"
    location: GeoLocation
    temperature: DailyTemperature
    humidity: float = Field(ge=0.0, le=100.0)
    rainfall_mm: float = Field(default=0.0, ge=0.0)
    wind_speed_kph: Optional[float] = Field(default=None, ge=0.0)
    missing_fields: List[str] = Field(default_factory=list)

class EnvironmentalMetricState(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )

    temperature_mean_24h: float
    temperature_mean_72h: float

    humidity_mean_24h: float
    humidity_mean_72h: float

    rainfall_24h: float = Field(default=0.0, ge=0.0)
    rainfall_72h: float = Field(default=0.0, ge=0.0)
    rainfall_7d: float = Field(default=0.0, ge=0.0)

    humid_hours_72h: int = Field(default=0, ge=0)

    heat_stress_hours_72h: int = Field(default=0, ge=0)

    cold_stress_hours_72h: int = Field(default=0, ge=0)


class ClimateState(DomainState):
    type: str = "ClimateState"

    location: GeoLocation

    current_conditions: HourlyClimateObservation

    degree_day: DegreeDay

    metrics: EnvironmentalMetricState

    accumulated_gdd: float = Field(
        default=0.0,
        ge=0.0,
    )

    anomalies: List[Anomaly] = Field(default_factory=list)

    environmental_events: List[EnvironmentalEventType] = Field(
        default_factory=list
    )

    reasoning: List[str] = Field(default_factory=list)

class HourlyClimateObservation(DomainState):
    type: str = "HourlyClimateObservation"
    location: GeoLocation
    temperature_c: float
    humidity: float = Field(ge=0.0, le=100.0)
    rainfall_mm: float = Field(default=0.0, ge=0.0)
    wind_speed_kph: Optional[float] = Field(default=None, ge=0.0)
    pressure_msl: Optional[float] = None
    cloud_cover_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )
    missing_fields: list[str] = Field(default_factory=list)


class CropStressState(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    heat_stress: SeverityLevel = SeverityLevel.MINOR
    water_stress: SeverityLevel = SeverityLevel.MINOR
    humidity_stress: SeverityLevel = SeverityLevel.MINOR
    cumulative_stress: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: List[str] = Field(default_factory=list)


class PhenologyState(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    biological_age_days: int = Field(default=0, ge=0)
    thermal_progression: float = Field(default=0.0, ge=0.0)
    development_completion_percentage: float = Field(default=0.0, ge=0.0, le=1.0)
    expected_next_transition: Optional[CropStageType] = None
    transition_confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class CropState(DomainState):
    type: str = "CropState"
    crop_id: str
    current_stage: CropStageType
    stage_started_at: date
    stage_duration_days: int = Field(default=0, ge=0)
    accumulated_development: float = Field(default=0.0, ge=0.0)
    accumulated_gdd: float = Field(default=0.0, ge=0.0)
    growth_velocity: float = Field(default=0.0, ge=0.0)
    stress_state: CropStressState = Field(default_factory=CropStressState)
    phenology: PhenologyState = Field(default_factory=PhenologyState)
    susceptibility_context: Dict[str, RiskLevel] = Field(default_factory=dict)
    microclimate_modifiers: Dict[str, float] = Field(default_factory=dict)
    reasoning: List[str] = Field(default_factory=list)


class PestState(DomainState):
    type: str = "PestState"
    pest_id: str
    current_stage: PestLifecycleStage
    accumulated_gdd: float = Field(default=0.0, ge=0.0)
    stage_progression_percentage: float = Field(default=0.0, ge=0.0, le=1.0)
    population_pressure: PopulationPressure
    outbreak_likelihood: float = Field(default=0.0, ge=0.0, le=1.0)
    outbreak_status: OutbreakStatus = OutbreakStatus.DORMANT
    trend_state: Trend = Field(default_factory=lambda: Trend(direction=TrendDirection.STABLE))
    biological_flags: List[BiologicalEventType] = Field(default_factory=list)
    reasoning: List[str] = Field(default_factory=list)


class EnvironmentalStability(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    stable_favorable_days: int = Field(default=0, ge=0)
    stable_unfavorable_days: int = Field(default=0, ge=0)
    volatility_score: float = Field(default=0.0, ge=0.0, le=1.0)
    persistence_strength: float = Field(default=0.0, ge=0.0, le=1.0)


class SuitabilityState(DomainState):
    type: str = "SuitabilityState"
    pest_id: str
    score: SuitabilityScore
    environmental_stability: EnvironmentalStability = Field(default_factory=EnvironmentalStability)
    contributing_factors: List[str] = Field(default_factory=list)
    limiting_factors: List[str] = Field(default_factory=list)
    evaluation_method: str = "weighted_suitability_v1"

    @property
    def overall_suitability(self) -> float:
        return self.score.overall_score


class RiskState(DomainState):
    type: str = "RiskState"
    pest_id: str
    risk_level: RiskLevel
    risk_score: float = Field(ge=0.0, le=1.0)
    urgency: UrgencyLevel
    severity: SeverityLevel
    outbreak_probability: float = Field(ge=0.0, le=1.0)
    expected_peak_window: Optional[TimeWindow] = None
    contributing_factors: List[str] = Field(default_factory=list)
    limiting_factors: List[str] = Field(default_factory=list)
    reasoning: List[str] = Field(default_factory=list)
    evaluation_method: str = "weighted_risk_v1"


class Recommendation(DomainState):
    type: str = "Recommendation"
    recommended_action: str
    intervention_type: InterventionType
    target_pest: str
    target_stage: PestLifecycleStage
    urgency: UrgencyLevel
    timing_window: Optional[TimeWindow] = None
    expected_effectiveness: float = Field(default=0.0, ge=0.0, le=1.0)
    expected_risk_reduction: float = Field(default=0.0, ge=0.0, le=1.0)
    status: RecommendationStatus = RecommendationStatus.GENERATED
    operational_notes: List[str] = Field(default_factory=list)
    reasoning: List[str] = Field(default_factory=list)
    alternative_options: List[str] = Field(default_factory=list)


class ForecastDay(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    simulation_date: date
    predicted_temperature: DailyTemperature
    predicted_humidity: float = Field(ge=0.0, le=100.0)
    predicted_rainfall_mm: float = Field(default=0.0, ge=0.0)
    predicted_wind_speed_kph: Optional[float] = Field(default=None, ge=0.0)
    forecast_confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class ClimateForecastTimeline(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )
    id: str = Field(default_factory=lambda: "climate_forecast_" + uuid4().hex)
    generated_at: datetime = Field(default_factory=utc_now)
    source: str
    projected_states: List[ClimateState]


ForecastClimateTimeline = ClimateForecastTimeline


class ProjectedDayState(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    simulation_date: date
    projected_climate_state: ClimateState
    projected_crop_state: CropState
    projected_pest_states: List[PestState]
    projected_suitability_states: List[SuitabilityState]
    projected_risk_states: List[RiskState]
    projected_recommendations: List[Recommendation]
    simulation_confidence: float = Field(ge=0.0, le=1.0)


class BiologicalForecastTimeline(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    id: str = Field(default_factory=lambda: "biological_forecast_" + uuid4().hex)
    generated_at: datetime = Field(default_factory=utc_now)
    projected_days: List[ProjectedDayState]
    outbreak_windows: List[TimeWindow] = Field(default_factory=list)
    intervention_windows: List[TimeWindow] = Field(default_factory=list)
    confidence_curve: List[float] = Field(default_factory=list)
    summary: List[str] = Field(default_factory=list)
