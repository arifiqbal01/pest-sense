from __future__ import annotations
from datetime import date, timedelta
from typing import Optional

from app.profiles import CropProfile, CropStageProfile
from app.domain.shared.enums import (
    CropStageType,
    EnvironmentalEventType,
    RiskLevel,
    SeverityLevel,
)
from app.domain.shared.contracts import (
    ClimateState,
    CropState,
    CropStressState,
    PhenologyState,
    SimulationContext,
)


class CropStateEngine:
    """
    Tracks crop biological development using thermal progression.
    """

    def initialize(
        self,
        crop_profile: CropProfile,
        sowing_date: date,
        context: Optional[SimulationContext] = None,
    ) -> CropState:
        first_stage = crop_profile.growth_model[0]

        simulation_date = (
            context.simulation_date
            if context
            else sowing_date
        )

        age_days = max(
            0,
            (simulation_date - sowing_date).days,
        )

        return self._build_state(
            crop_profile=crop_profile,
            stage=first_stage,
            simulation_date=simulation_date,
            sowing_date=sowing_date,
            accumulated_gdd=0.0,
            confidence=0.75,
            source="initialization",
            reasoning=[
                "Crop cycle initialized from sowing date."
            ],
        )

    def initialize_from_inference(
            self,
            crop_profile: CropProfile,
            inferred_stage: CropStageType,
            biological_age_days: int,
            climate_state: ClimateState,
            context: Optional[SimulationContext] = None,
    ) -> CropState:
        """
        Region-aware initialization for current-state inference.

        Produces biologically consistent crop state instead of
        initializing at germination then mutating stage later.
        """
        stage = self._profile_stage(
            crop_profile,
            inferred_stage,
        )

        simulation_date = (
            context.simulation_date
            if context
            else climate_state.timestamp.date()
        )

        accumulated_gdd = stage.gdd_requirement

        confidence = min(
            0.72,
            climate_state.confidence,
        )

        estimated_sowing_date = simulation_date - timedelta(
            days=biological_age_days
        )

        return self._build_state(
            crop_profile=crop_profile,
            stage=stage,
            simulation_date=simulation_date,
            sowing_date=estimated_sowing_date,
            accumulated_gdd=accumulated_gdd,
            confidence=confidence,
            source=climate_state.source,
            reasoning=[
                (
                    f"Crop initialized from regional inference at "
                    f"stage {stage.name} "
                    f"with estimated biological age "
                    f"{biological_age_days} days."
                )
            ],
        )

    def initialize_crop_cycle(
        self,
        crop_profile: CropProfile,
        sowing_date: date,
        context: Optional[SimulationContext] = None,
    ) -> CropState:
        return self.initialize(
            crop_profile=crop_profile,
            sowing_date=sowing_date,
            context=context,
        )

    def advance(
        self,
        previous_state: CropState,
        climate_state: ClimateState,
        crop_profile: CropProfile,
        context: Optional[SimulationContext] = None,
    ) -> CropState:
        simulation_date = (
            context.simulation_date
            if context
            else climate_state.timestamp.date()
        )

        stress_state = self._stress_state(
            climate_state,
            crop_profile,
        )

        suppression = self._development_suppression(
            climate_state,
            stress_state,
        )

        effective_daily_gdd = (
            climate_state.degree_day.daily_value
            * (1.0 - suppression)
        )

        accumulated_gdd = (
            previous_state.accumulated_gdd
            + effective_daily_gdd
        )

        stage = self._stage_for_gdd(
            crop_profile,
            accumulated_gdd,
        )

        previous_stage = self._profile_stage(
            crop_profile,
            CropStageType(previous_state.current_stage),
        )

        stage_started_at = previous_state.stage_started_at
        reasoning = list(previous_state.reasoning[-3:])

        if str(stage.name) != str(previous_stage.name):
            stage_started_at = simulation_date
            reasoning.append(
                f"Crop transitioned from "
                f"{previous_stage.name} to {stage.name} "
                f"based on accumulated GDD."
            )
        else:
            reasoning.append(
                f"Crop remained in {stage.name}; "
                f"accumulated GDD is {accumulated_gdd:.1f}."
            )

        completion = self._stage_completion(
            crop_profile,
            stage,
            accumulated_gdd,
        )

        confidence = min(
            previous_state.confidence,
            climate_state.confidence,
        )

        if context:
            confidence *= context.confidence_modifier

        age_days = max(
            0,
            (simulation_date - previous_state.stage_started_at).days,
        )

        return CropState(
            id=f"crop_state_{crop_profile.id}_{simulation_date.isoformat()}",
            timestamp=climate_state.timestamp,
            source=climate_state.source,
            confidence=confidence,
            crop_id=crop_profile.id,
            current_stage=stage.name,
            stage_started_at=stage_started_at,
            stage_duration_days=age_days,
            accumulated_development=completion,
            accumulated_gdd=accumulated_gdd,
            growth_velocity=effective_daily_gdd,
            stress_state=stress_state,
            phenology=PhenologyState(
                biological_age_days=(
                    previous_state.phenology.biological_age_days + 1
                ),
                thermal_progression=accumulated_gdd,
                development_completion_percentage=completion,
                expected_next_transition=self._next_stage_name(
                    crop_profile,
                    stage,
                ),
                transition_confidence=confidence,
            ),
            susceptibility_context=self._susceptibility_context(
                crop_profile,
                stage,
            ),
            microclimate_modifiers=stage.microclimate_effects,
            reasoning=(
                reasoning
                + stress_state.reasoning
                + self._suppression_reasoning(suppression)
            ),
        )

    def simulate(
        self,
        previous_state: CropState,
        climate_state: ClimateState,
        crop_profile: CropProfile,
        context: Optional[SimulationContext] = None,
    ) -> CropState:
        return self.advance(
            previous_state=previous_state,
            climate_state=climate_state,
            crop_profile=crop_profile,
            context=context,
        )

    def _build_state(
        self,
        crop_profile: CropProfile,
        stage: CropStageProfile,
        simulation_date: date,
        sowing_date: date,
        accumulated_gdd: float,
        confidence: float,
        source: str,
        reasoning: list[str],
    ) -> CropState:
        age_days = max(
            0,
            (simulation_date - sowing_date).days,
        )

        completion = self._stage_completion(
            crop_profile,
            stage,
            accumulated_gdd,
        )

        return CropState(
            id=f"crop_state_{crop_profile.id}_{simulation_date.isoformat()}",
            timestamp=simulation_date,
            source=source,
            confidence=confidence,
            crop_id=crop_profile.id,
            current_stage=stage.name,
            stage_started_at=simulation_date,
            stage_duration_days=0,
            accumulated_development=completion,
            accumulated_gdd=accumulated_gdd,
            growth_velocity=0.0,
            stress_state=CropStressState(),
            phenology=PhenologyState(
                biological_age_days=age_days,
                thermal_progression=accumulated_gdd,
                development_completion_percentage=completion,
                expected_next_transition=self._next_stage_name(
                    crop_profile,
                    stage,
                ),
                transition_confidence=confidence,
            ),
            susceptibility_context=self._susceptibility_context(
                crop_profile,
                stage,
            ),
            microclimate_modifiers=stage.microclimate_effects,
            reasoning=reasoning,
        )

    def _stage_for_gdd(
        self,
        crop_profile: CropProfile,
        accumulated_gdd: float,
    ) -> CropStageProfile:
        current = crop_profile.growth_model[0]

        for stage in crop_profile.growth_model:
            if accumulated_gdd >= stage.gdd_requirement:
                current = stage

        return current

    def _profile_stage(
        self,
        crop_profile: CropProfile,
        stage_name: CropStageType,
    ) -> CropStageProfile:
        for stage in crop_profile.growth_model:
            if stage.name == stage_name:
                return stage

        return crop_profile.growth_model[0]

    def _next_stage_name(
        self,
        crop_profile: CropProfile,
        current_stage: CropStageProfile,
    ) -> Optional[CropStageType]:
        next_order = current_stage.order + 1

        for stage in crop_profile.growth_model:
            if stage.order == next_order:
                return stage.name

        return None

    def _stage_completion(
        self,
        crop_profile: CropProfile,
        stage: CropStageProfile,
        accumulated_gdd: float,
    ) -> float:
        previous_requirement = 0.0

        for candidate in crop_profile.growth_model:
            if candidate.order == stage.order - 1:
                previous_requirement = candidate.gdd_requirement
                break

        span = max(
            1.0,
            stage.gdd_requirement - previous_requirement,
        )

        return max(
            0.0,
            min(
                1.0,
                (accumulated_gdd - previous_requirement) / span,
            ),
        )

    def _susceptibility_context(
        self,
        crop_profile: CropProfile,
        stage: CropStageProfile,
    ) -> dict[str, RiskLevel]:
        stage_key = stage.name.value

        level_map = {
            "low": RiskLevel.LOW,
            "moderate": RiskLevel.MODERATE,
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL,
        }

        return {
            pest_id: level_map.get(
                stages.get(stage_key, "low"),
                RiskLevel.LOW,
            )
            for pest_id, stages in crop_profile.pest_susceptibility.items()
        }

    def _stress_state(
        self,
        climate_state: ClimateState,
        crop_profile: CropProfile,
    ) -> CropStressState:
        heat_limit = crop_profile.stress_thresholds.get(
            "heat_stress_limit",
            38,
        )

        severe_heat = crop_profile.stress_thresholds.get(
            "severe_heat_stress_limit",
            42,
        )

        current_temp = climate_state.current_conditions.temperature_c

        rainfall_limit = crop_profile.stress_thresholds.get(
            "low_rainfall_7_day_mm",
            5,
        )

        recent_rainfall = climate_state.metrics.rainfall_7d

        heat_stress = SeverityLevel.MINOR
        cumulative = 0.0
        reasoning = []

        if current_temp >= severe_heat:
            heat_stress = SeverityLevel.SEVERE
            cumulative = 0.8
            reasoning.append("Severe heat stress may slow crop development.")
        elif current_temp >= heat_limit:
            heat_stress = SeverityLevel.MODERATE
            cumulative = 0.45
            reasoning.append("Moderate heat stress detected.")

        water_stress = (
            SeverityLevel.MODERATE
            if recent_rainfall < rainfall_limit
            else SeverityLevel.MINOR
        )

        if water_stress != SeverityLevel.MINOR:
            reasoning.append("Recent rainfall below crop threshold.")

        humidity_stress = SeverityLevel.MINOR

        if climate_state.metrics.humidity_mean_24h >= 90:
            humidity_stress = SeverityLevel.MODERATE
            reasoning.append("High humidity stress detected.")

        cumulative = min(
            1.0,
            cumulative + (
                0.2
                if water_stress != SeverityLevel.MINOR
                else 0.0
            ),
        )

        return CropStressState(
            heat_stress=heat_stress,
            water_stress=water_stress,
            humidity_stress=humidity_stress,
            cumulative_stress=cumulative,
            reasoning=reasoning,
        )

    def _development_suppression(
        self,
        climate_state: ClimateState,
        stress_state: CropStressState,
    ) -> float:
        suppression = stress_state.cumulative_stress * 0.45

        events = {
            str(event)
            for event in climate_state.environmental_events
        }

        if EnvironmentalEventType.HEATWAVE.value in events:
            suppression += 0.18

        if EnvironmentalEventType.DROUGHT.value in events:
            suppression += 0.16

        if EnvironmentalEventType.HEAVY_RAINFALL.value in events:
            suppression += 0.08

        return max(0.0, min(0.75, suppression))

    def _suppression_reasoning(
        self,
        suppression: float,
    ) -> list[str]:
        if suppression <= 0.05:
            return [
                "Thermal development proceeded without meaningful environmental suppression."
            ]

        return [
            (
                "Effective crop development was reduced by "
                f"{suppression:.0%} from stress and environmental forcing."
            )
        ]
