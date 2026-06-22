from __future__ import annotations

from datetime import date
from typing import List, Optional

from app.domain.crop import CropStateEngine
from app.domain.inference.contracts import (
    InferredCurrentState,
    RegionalCropInference,
    RegionalPestInference,
    SeasonalAssumptions,
)
from app.domain.pest import PestStateEngine
from app.profiles import CropProfile, PestProfile, RegionProfile
from app.domain.shared.enums import (
    CropStageType,
    EnvironmentType,
    PestLifecycleStage,
    RiskLevel,
    SimulationMode,
    TrendDirection,
)
from app.domain.shared.contracts import (
    ClimateState,
    CropState,
    PestState,
    SimulationContext,
)
from app.domain.shared.value_objects import PopulationPressure


class CurrentStateInferenceEngine:
    """
    Region-aware biological state inference.

    MVP purpose:
    infer plausible CURRENT biological state
    from regional seasonal assumptions when
    farm observations do not exist.
    """

    def __init__(
        self,
        crop_engine: Optional[CropStateEngine] = None,
        pest_engine: Optional[PestStateEngine] = None,
    ) -> None:
        self.crop_engine = crop_engine or CropStateEngine()
        self.pest_engine = pest_engine or PestStateEngine()

    def infer(
        self,
        climate_state: ClimateState,
        region_profile: RegionProfile,
        crop_profile: CropProfile,
        pest_profiles: List[PestProfile],
        context: SimulationContext,
    ) -> InferredCurrentState:
        seasonal = SeasonalAssumptions.model_validate(
            self._normalize_seasonal_assumptions(
                region_profile.seasonal_assumptions
            )
        )

        crop_inference = self._build_crop_inference(
            seasonal=seasonal,
            simulation_date=context.simulation_date,
        )

        crop_state = self._infer_crop_state(
            climate_state=climate_state,
            crop_profile=crop_profile,
            crop_inference=crop_inference,
            region_profile=region_profile,
            context=context,
        )

        pest_states: List[PestState] = []
        pest_inferences: List[RegionalPestInference] = []

        for pest_profile in pest_profiles:
            pest_inference = self._build_pest_inference(
                pest_profile=pest_profile,
                region_profile=region_profile,
                crop_state=crop_state,
            )

            pest_state = self._infer_pest_state(
                pest_profile=pest_profile,
                pest_inference=pest_inference,
                climate_state=climate_state,
                crop_state=crop_state,
                context=context,
            )

            pest_states.append(pest_state)
            pest_inferences.append(pest_inference)

        confidence = self._calculate_confidence(
            crop_inference=crop_inference,
            pest_inferences=pest_inferences,
        )

        return InferredCurrentState(
            crop_state=crop_state,
            pest_states=pest_states,
            crop_inference=crop_inference,
            pest_inferences=pest_inferences,
            confidence=confidence,
            assumptions=[
                "Region-level biological inference used.",
                "Farm observations unavailable.",
                "Regional seasonal assumptions applied.",
            ],
        )

    def _build_crop_inference(
        self,
        seasonal: SeasonalAssumptions,
        simulation_date: date,
    ) -> RegionalCropInference:
        inferred_stage = self._infer_crop_stage(
            simulation_date=simulation_date,
            seasonal=seasonal,
        )

        estimated_age_days = self._estimated_crop_age_days(
            inferred_stage
        )

        return RegionalCropInference(
            inferred_stage=inferred_stage,
            estimated_age_days=estimated_age_days,
            confidence=0.72,
            reasoning=[
                f"Regional seasonal calendar indicates {inferred_stage.value} stage."
            ],
        )

    def _infer_crop_state(
        self,
        climate_state: ClimateState,
        crop_profile: CropProfile,
        crop_inference: RegionalCropInference,
        region_profile: RegionProfile,
        context: SimulationContext,
    ) -> CropState:
        crop_state = self.crop_engine.initialize_from_inference(
            crop_profile=crop_profile,
            inferred_stage=crop_inference.inferred_stage,
            biological_age_days=crop_inference.estimated_age_days,
            climate_state=climate_state,
            context=context,
        )

        if (
            region_profile.environment_type
            == EnvironmentType.OPEN_FIELD_IRRIGATED_AGRICULTURE
        ):
            crop_state.reasoning.append(
                "Irrigated region assumptions applied."
            )

        return crop_state

    def _build_pest_inference(
        self,
        pest_profile: PestProfile,
        region_profile: RegionProfile,
        crop_state: CropState,
    ) -> RegionalPestInference:
        pressure_profiles = (
            region_profile.pest_patterns.get(
                "pressure_profiles",
                {},
            )
        )

        pest_key = pest_profile.id.replace("pest_", "")
        pressure_hint = pressure_profiles.get(pest_key)

        inferred_stage = self._infer_pest_stage(
            crop_state.current_stage,
            pressure_hint,
        )

        outbreak_potential = self._infer_outbreak_potential(
            pressure_hint
        )

        reasoning = []

        if pressure_hint:
            reasoning.append(
                f"Regional pressure profile: {pressure_hint}"
            )

        reasoning.append(
            f"Crop stage context: {crop_state.current_stage}"
        )

        return RegionalPestInference(
            pest_id=pest_profile.id,
            inferred_stage=inferred_stage,
            outbreak_potential=outbreak_potential,
            confidence=0.68,
            reasoning=reasoning,
        )

    def _infer_pest_state(
        self,
        pest_profile: PestProfile,
        pest_inference: RegionalPestInference,
        climate_state: ClimateState,
        crop_state: CropState,
        context: SimulationContext,
    ) -> PestState:
        return self.pest_engine.initialize_from_inference(
            pest_profile=pest_profile,
            inferred_stage=pest_inference.inferred_stage,
            accumulated_gdd=self._estimated_pest_gdd(
                pest_profile,
                pest_inference.inferred_stage,
            ),
            population_pressure=PopulationPressure(
                level=self._pressure_level(
                    pest_inference.outbreak_potential
                ),
                growth_rate=0.1,
                trend=TrendDirection.STABLE,
                outbreak_potential=pest_inference.outbreak_potential,
            ),
            climate_state=climate_state,
            context=context,
        )

    def _infer_crop_stage(
        self,
        simulation_date: date,
        seasonal: SeasonalAssumptions,
    ) -> CropStageType:
        month_day = simulation_date.strftime("%m-%d")

        if self._in_window(
            month_day,
            seasonal.cotton_establishment_window,
        ):
            return CropStageType.SEEDLING

        if self._in_window(
            month_day,
            seasonal.vegetative_growth_window,
        ):
            return CropStageType.VEGETATIVE

        if self._in_window(
            month_day,
            seasonal.flowering_window,
        ):
            return CropStageType.FLOWERING

        if self._in_window(
            month_day,
            seasonal.boll_formation_window,
        ):
            return CropStageType.BOLL_FORMATION

        if self._in_window(
            month_day,
            seasonal.harvest_window,
        ):
            return CropStageType.MATURITY

        return CropStageType.GERMINATION

    def _infer_pest_stage(
        self,
        crop_stage: CropStageType,
        pressure_hint: Optional[str],
    ) -> PestLifecycleStage:
        if crop_stage in {
            CropStageType.FLOWERING,
            CropStageType.BOLL_FORMATION,
        }:
            return PestLifecycleStage.ADULT

        if crop_stage == CropStageType.VEGETATIVE:
            return PestLifecycleStage.NYMPH

        return PestLifecycleStage.EGG

    def _estimated_crop_age_days(
        self,
        stage: CropStageType,
    ) -> int:
        mapping = {
            CropStageType.GERMINATION: 5,
            CropStageType.SEEDLING: 18,
            CropStageType.VEGETATIVE: 50,
            CropStageType.FLOWERING: 85,
            CropStageType.BOLL_FORMATION: 120,
            CropStageType.MATURITY: 160,
        }
        return mapping.get(stage, 10)

    def _estimated_pest_gdd(
        self,
        pest_profile: PestProfile,
        stage: PestLifecycleStage,
    ) -> float:
        for lifecycle in pest_profile.lifecycle_model:
            if lifecycle.name == stage:
                return lifecycle.required_gdd
        return 0.0

    def _infer_outbreak_potential(
        self,
        pressure_hint: Optional[str],
    ) -> float:
        if not pressure_hint:
            return 0.2

        mapping = {
            "very_high_in_hot_humid_irrigated_periods": 0.75,
            "high_during_vegetative_and_early_flowering": 0.60,
            "moderate_high_in_hot_dry_early_crop_stage": 0.45,
            "episodic_outbreaks_in_moderate_conditions": 0.35,
            "localized_but_high_when_established": 0.40,
            "high_during_boll_formation_and_late_crop": 0.65,
        }

        return mapping.get(pressure_hint, 0.25)

    def _pressure_level(
        self,
        potential: float,
    ) -> RiskLevel:
        if potential >= 0.75:
            return RiskLevel.HIGH
        if potential >= 0.45:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    def _in_window(
        self,
        month_day: str,
        window,
    ) -> bool:
        if window is None:
            return False

        return (
            window.start_mm_dd
            <= month_day
            <= window.end_mm_dd
        )

    def _normalize_seasonal_assumptions(
        self,
        raw: dict,
    ) -> dict:
        normalized = {}

        for key, value in raw.items():
            if isinstance(value, list) and len(value) == 2:
                normalized[key] = {
                    "start_mm_dd": value[0],
                    "end_mm_dd": value[1],
                }
            else:
                normalized[key] = value

        return normalized

    def _calculate_confidence(
        self,
        crop_inference: RegionalCropInference,
        pest_inferences: List[RegionalPestInference],
    ) -> float:
        values = [crop_inference.confidence]
        values.extend(p.confidence for p in pest_inferences)

        return min(values) if values else 0.5