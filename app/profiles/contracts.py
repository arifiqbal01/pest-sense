# app/profiles/contracts.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.shared.enums import (
    CropStageType,
    EnvironmentType,
    InterventionType,
    PestCategory,
    PestLifecycleStage,
)
from app.shared.value_objects import GeoLocation

class ProfileModel(BaseModel):
    """
    Base schema for profile contracts.
    Allows forward-compatible JSON profile evolution.
    """
    model_config = ConfigDict(
        extra="allow",
    )


class BaseProfile(ProfileModel):
    id: str
    type: str
    version: str = "1.0"
    name: str

    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Range(ProfileModel):
    minimum: float
    maximum: float

    @model_validator(mode="after")
    def validate_order(self) -> "Range":
        if self.maximum < self.minimum:
            raise ValueError("range maximum must be >= minimum")
        return self


class ThermalProperties(ProfileModel):
    base_temperature: float
    upper_temperature_threshold: float
    optimal_temperature_range: Range
    lethal_temperature_range: Optional[Range] = None


class HumidityPreferences(ProfileModel):
    optimal_humidity_range: Range
    humidity_stress_threshold: Optional[Any] = None


class VulnerabilityProfile(ProfileModel):
    chemical_vulnerability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )
    biological_vulnerability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )


class LifecycleStageProfile(ProfileModel):
    name: PestLifecycleStage
    order: int = Field(ge=0)
    required_gdd: float = Field(ge=0.0)

    feeding_behavior: str = "unknown"
    reproduction_capability: bool = False
    mobility: str = "unknown"

    vulnerability: VulnerabilityProfile = Field(
        default_factory=VulnerabilityProfile
    )

    economic_damage_weight: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )


class ReproductionModel(ProfileModel):
    reproduction_rate: float = Field(
        default=0.0,
        ge=0.0,
    )
    generation_overlap_possible: bool = False


class DamageProfile(ProfileModel):
    critical_damage_stages: List[PestLifecycleStage] = Field(
        default_factory=list
    )
    crop_damage_types: List[str] = Field(
        default_factory=list
    )
    severity_weights: Dict[str, float] = Field(
        default_factory=dict
    )


class SuitabilityWeights(ProfileModel):
    temperature: float = Field(default=0.5, ge=0.0)
    humidity: float = Field(default=0.3, ge=0.0)
    rainfall: float = Field(default=0.2, ge=0.0)


class PestProfile(BaseProfile):
    type: str = "PestProfile"

    scientific_name: str
    pest_category: PestCategory

    thermal_properties: ThermalProperties
    humidity_preferences: HumidityPreferences

    lifecycle_model: List[LifecycleStageProfile]

    reproduction_model: ReproductionModel = Field(
        default_factory=ReproductionModel
    )

    damage_profile: DamageProfile = Field(
        default_factory=DamageProfile
    )

    suitability_weights: SuitabilityWeights = Field(
        default_factory=SuitabilityWeights
    )

    crop_stage_modifiers: Dict[str, Dict[str, float]] = Field(
        default_factory=dict
    )

    intervention_sensitivity: Dict[str, Any] = Field(
        default_factory=dict
    )

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "PestProfile":
        ordered = sorted(
            self.lifecycle_model,
            key=lambda stage: stage.order,
        )

        if ordered != self.lifecycle_model:
            raise ValueError(
                "pest lifecycle stages must be ordered by order"
            )

        return self


class CropStageProfile(ProfileModel):
    name: CropStageType
    order: int = Field(ge=0)

    expected_duration_days: int = Field(ge=0)
    gdd_requirement: float = Field(ge=0.0)

    vulnerable_pests: List[str] = Field(default_factory=list)

    economic_importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    microclimate_effects: Dict[str, float] = Field(
        default_factory=dict
    )


class CropProfile(BaseProfile):
    type: str = "CropProfile"

    crop_type: str
    cultivar: Optional[str] = None

    thermal_base_temperature: float = 12.0

    growth_model: List[CropStageProfile]

    pest_susceptibility: Dict[str, Dict[str, str]] = Field(
        default_factory=dict
    )

    stress_thresholds: Dict[str, float] = Field(
        default_factory=dict
    )

    economic_profile: Dict[str, Any] = Field(
        default_factory=dict
    )


class AdministrativeRegion(ProfileModel):
    country: str
    province: str
    district: str
    tehsil: str

class RegionProfile(BaseProfile):
    type: str = "RegionProfile"

    geographic_zone: AdministrativeRegion
    weather_location: GeoLocation

    environment_type: EnvironmentType = (
        EnvironmentType.OPEN_FIELD
    )

    climate_behavior: Dict[str, Any] = Field(
        default_factory=dict
    )

    seasonal_assumptions: Dict[str, Any] = Field(
        default_factory=dict
    )

    pest_patterns: Dict[str, Any] = Field(
        default_factory=dict
    )

    environmental_modifiers: Dict[str, float] = Field(
        default_factory=dict
    )


class EffectivenessModel(ProfileModel):
    expected_reduction: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    delayed_effect_days: int = Field(
        default=0,
        ge=0,
    )

    persistence_days: int = Field(
        default=0,
        ge=0,
    )


class TreatmentProfile(BaseProfile):
    type: str = "TreatmentProfile"

    treatment_type: InterventionType

    target_pests: List[str] = Field(
        default_factory=list
    )

    target_lifecycle_stages: List[PestLifecycleStage] = Field(
        default_factory=list
    )

    effectiveness_model: EffectivenessModel = Field(
        default_factory=EffectivenessModel
    )

    environmental_constraints: Dict[str, Any] = Field(
        default_factory=dict
    )

    resistance_profile: Dict[str, Any] = Field(
        default_factory=dict
    )

    economic_profile: Dict[str, Any] = Field(
        default_factory=dict
    )