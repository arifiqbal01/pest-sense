from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import Field

from .base import ApiModel

from app.shared.kernel import (
    ClimateState,
    CropState,
    PestState,
    Recommendation,
    RiskState,
    SuitabilityState,
)
from app.shared.value_objects import TimeWindow


# =========================
# REQUESTS
# =========================

class CurrentAnalysisRequest(ApiModel):
    region: str = Field(
        description="Region profile identifier",
        examples=["region_khanpur_tehsil"],
    )

    crop: str = Field(
        description="Crop profile identifier",
        examples=["crop_cotton"],
    )

    pests: Optional[List[str]] = Field(
        default=None,
        description="Optional pest profile identifiers",
        examples=[["pest_whitefly", "pest_jassid"]],
    )


class ForecastAnalysisRequest(ApiModel):
    region: str = Field(
        description="Region profile identifier",
        examples=["region_khanpur_tehsil"],
    )

    crop: str = Field(
        description="Crop profile identifier",
        examples=["crop_cotton"],
    )

    pests: Optional[List[str]] = Field(
        default=None,
        description="Optional pest profile identifiers",
    )

    forecast_days: int = Field(
        default=14,
        ge=1,
        le=30,
        description="Forecast horizon in days",
    )


# =========================
# CURRENT ANALYSIS RESPONSE
# =========================

class CurrentAnalysisResponse(ApiModel):
    climate_state: ClimateState
    crop_state: CropState
    pest_states: List[PestState]
    suitability_states: List[SuitabilityState]
    risk_states: List[RiskState]
    recommendations: List[Recommendation]


# =========================
# FORECAST RESPONSE
# =========================

class ForecastDayResponse(ApiModel):
    simulation_date: date
    simulation_confidence: float
    projected_climate_state: ClimateState
    projected_crop_state: CropState
    projected_pest_states: List[PestState]
    projected_suitability_states: List[SuitabilityState]
    projected_risk_states: List[RiskState]
    projected_recommendations: List[Recommendation]


class ForecastAnalysisResponse(ApiModel):
    projected_days: List[ForecastDayResponse]
    confidence_curve: List[float]
    outbreak_windows: List[TimeWindow] = Field(default_factory=list)
    intervention_windows: List[TimeWindow] = Field(default_factory=list)
    summary: List[str] = Field(default_factory=list)