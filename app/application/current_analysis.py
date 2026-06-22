from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.domain.climate import ClimateEngine
from app.domain.climate.contracts.weather_context import WeatherContext
from app.domain.inference import CurrentStateInferenceEngine
from app.domain.recommendation import RecommendationEngine
from app.domain.risk import RiskEngine
from app.domain.suitability import SuitabilityEngine
from app.profiles import (
    CropProfile,
    PestProfile,
    ProfileRegistry,
    RegionProfile,
)
from app.shared.enums import SimulationMode
from app.shared.kernel import (
    ClimateState,
    CropState,
    PestState,
    Recommendation,
    RiskState,
    SimulationContext,
    SuitabilityState,
)


class CurrentAnalysisResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )

    climate_state: ClimateState
    crop_state: CropState
    pest_states: List[PestState]
    suitability_states: List[SuitabilityState]
    risk_states: List[RiskState]
    recommendations: List[Recommendation]


class CurrentAnalysisWorkflow:
    """
    Current biological analysis orchestration.

    Responsibilities:
    - compute current climate intelligence
    - infer current biological crop state
    - infer current biological pest states
    - evaluate suitability
    - evaluate risk
    - generate recommendations

    This workflow orchestrates only.
    Biological inference belongs to domain inference engine.
    """

    def __init__(
        self,
        profile_registry: ProfileRegistry,
        climate_engine: Optional[ClimateEngine] = None,
        inference_engine: Optional[CurrentStateInferenceEngine] = None,
        suitability_engine: Optional[SuitabilityEngine] = None,
        risk_engine: Optional[RiskEngine] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
    ) -> None:
        self.profile_registry = profile_registry
        self.climate_engine = climate_engine or ClimateEngine()
        self.inference_engine = (
            inference_engine or CurrentStateInferenceEngine()
        )
        self.suitability_engine = suitability_engine or SuitabilityEngine()
        self.risk_engine = risk_engine or RiskEngine()
        self.recommendation_engine = (
            recommendation_engine or RecommendationEngine()
        )

    def run(
        self,
        weather_context: WeatherContext,
        region_profile: RegionProfile,
        crop_profile: CropProfile,
        pest_profiles: List[PestProfile],
    ) -> CurrentAnalysisResult:
        simulation_date = weather_context.current.timestamp.date()

        context = SimulationContext(
            mode=SimulationMode.CURRENT,
            simulation_date=simulation_date,
            source=weather_context.source,
        )

        climate_state = self.climate_engine.compute_current_state(
            weather_context=weather_context,
            base_temperature=crop_profile.thermal_base_temperature,
        )

        inferred = self.inference_engine.infer(
            climate_state=climate_state,
            region_profile=region_profile,
            crop_profile=crop_profile,
            pest_profiles=pest_profiles,
            context=context,
        )

        crop_state = inferred.crop_state
        pest_states = inferred.pest_states

        suitability_states: List[SuitabilityState] = []
        risk_states: List[RiskState] = []
        recommendations: List[Recommendation] = []

        for pest_profile, pest_state in zip(
            pest_profiles,
            pest_states,
        ):
            suitability_state = self.suitability_engine.evaluate(
                pest_profile=pest_profile,
                climate_state=climate_state,
                crop_state=crop_state,
                pest_state=pest_state,
            )

            risk_state = self.risk_engine.evaluate(
                pest_profile=pest_profile,
                pest_state=pest_state,
                crop_state=crop_state,
                suitability_state=suitability_state,
                climate_state=climate_state,
            )

            recommendation = self.recommendation_engine.generate(
                pest_profile=pest_profile,
                risk_state=risk_state,
                pest_state=pest_state,
                crop_state=crop_state,
                treatment_profiles=(
                    self.profile_registry
                    .treatment_profiles_for_pest(
                        pest_profile.id
                    )
                ),
            )

            suitability_states.append(suitability_state)
            risk_states.append(risk_state)
            recommendations.append(recommendation)

        return CurrentAnalysisResult(
            climate_state=climate_state,
            crop_state=crop_state,
            pest_states=pest_states,
            suitability_states=suitability_states,
            risk_states=risk_states,
            recommendations=recommendations,
        )