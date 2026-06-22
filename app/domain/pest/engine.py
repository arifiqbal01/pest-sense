from __future__ import annotations

from typing import Optional

from app.profiles import LifecycleStageProfile, PestProfile
from app.domain.shared.enums import (
    BiologicalEventType,
    EnvironmentalEventType,
    OutbreakStatus,
    PestLifecycleStage,
    RiskLevel,
    TrendDirection,
)
from app.domain.shared.contracts import (
    ClimateState,
    CropState,
    PestState,
    SimulationContext,
    SuitabilityState,
)
from app.domain.shared.value_objects import PopulationPressure, Trend


class PestStateEngine:
    """
    Models pest lifecycle progression and outbreak pressure.
    """

    def initialize(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        context: Optional[SimulationContext] = None,
    ) -> PestState:
        first_stage = pest_profile.lifecycle_model[0]

        simulation_date = (
            context.simulation_date
            if context
            else climate_state.timestamp.date()
        )

        return self._build_state(
            pest_profile=pest_profile,
            stage=first_stage,
            simulation_date=simulation_date,
            climate_state=climate_state,
            accumulated_gdd=0.0,
            population_pressure=PopulationPressure(
                level=RiskLevel.LOW,
                growth_rate=0.0,
                trend=TrendDirection.STABLE,
                outbreak_potential=0.1,
            ),
            confidence=min(0.75, climate_state.confidence),
            reasoning=[
                "Pest state initialized at earliest lifecycle stage."
            ],
        )

    def initialize_from_inference(
        self,
        pest_profile: PestProfile,
        inferred_stage: PestLifecycleStage,
        accumulated_gdd: float,
        population_pressure: PopulationPressure,
        climate_state: ClimateState,
        context: Optional[SimulationContext] = None,
    ) -> PestState:
        """
        Region-aware biological initialization.

        Used for current-state inference where pest populations
        already exist in the ecosystem.
        """
        simulation_date = (
            context.simulation_date
            if context
            else climate_state.timestamp.date()
        )

        stage = self._profile_stage(
            pest_profile,
            inferred_stage,
        )

        return self._build_state(
            pest_profile=pest_profile,
            stage=stage,
            simulation_date=simulation_date,
            climate_state=climate_state,
            accumulated_gdd=accumulated_gdd,
            population_pressure=population_pressure,
            confidence=min(0.68, climate_state.confidence),
            reasoning=[
                f"Pest initialized from regional inference at stage {stage.name}."
            ],
        )

    def initialize_pest_state(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        context: Optional[SimulationContext] = None,
    ) -> PestState:
        return self.initialize(
            pest_profile=pest_profile,
            climate_state=climate_state,
            context=context,
        )

    def advance(
        self,
        previous_state: PestState,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        crop_state: CropState,
        context: Optional[SimulationContext] = None,
    ) -> PestState:
        simulation_date = (
            context.simulation_date
            if context
            else climate_state.timestamp.date()
        )

        biological_viability = self._biological_viability(
            pest_profile,
            climate_state,
            crop_state,
        )

        daily_gdd = (
            climate_state.degree_day.daily_value
            * self._thermal_response(
                pest_profile,
                climate_state,
            )
            * biological_viability
        )

        accumulated_gdd = (
            previous_state.accumulated_gdd + daily_gdd
        )

        stage = self._stage_for_gdd(
            pest_profile,
            accumulated_gdd,
        )

        previous_stage = PestLifecycleStage(
            previous_state.current_stage
        )

        reasoning = list(previous_state.reasoning[-3:])

        stage_name = self._stage_name(stage.name)
        previous_stage_name = self._stage_name(previous_stage)

        if stage_name != previous_stage_name:
            reasoning.append(
                f"{pest_profile.name} transitioned from "
                f"{previous_stage_name} to {stage_name} "
                f"from accumulated thermal progression."
            )
        else:
            reasoning.append(
                f"{pest_profile.name} remained in "
                f"{stage_name}; accumulated GDD is "
                f"{accumulated_gdd:.1f}."
            )

        if stage.reproduction_capability:
            reasoning.append(
                f"{stage_name} stage can reproduce."
            )

        if biological_viability < 0.65:
            reasoning.append(
                "Environmental or host suppression slowed pest biological progression."
            )

        population_pressure = self._population_pressure(
            previous_state=previous_state,
            pest_profile=pest_profile,
            stage=stage,
            climate_state=climate_state,
            crop_state=crop_state,
            biological_viability=biological_viability,
        )

        outbreak_likelihood = self._outbreak_likelihood(
            population_pressure,
            stage,
        )

        confidence = min(
            previous_state.confidence,
            climate_state.confidence,
        )

        if context:
            confidence *= context.confidence_modifier

        return self._build_state(
            pest_profile=pest_profile,
            stage=stage,
            simulation_date=simulation_date,
            climate_state=climate_state,
            accumulated_gdd=accumulated_gdd,
            population_pressure=population_pressure,
            confidence=confidence,
            reasoning=reasoning,
        )

    def simulate(
        self,
        previous_state: PestState,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        crop_state: CropState,
        suitability_state: Optional[SuitabilityState] = None,
        context: Optional[SimulationContext] = None,
    ) -> PestState:
        return self.advance(
            previous_state=previous_state,
            pest_profile=pest_profile,
            climate_state=climate_state,
            crop_state=crop_state,
            context=context,
        )

    def _build_state(
        self,
        pest_profile: PestProfile,
        stage: LifecycleStageProfile,
        simulation_date,
        climate_state: ClimateState,
        accumulated_gdd: float,
        population_pressure: PopulationPressure,
        confidence: float,
        reasoning: list[str],
    ) -> PestState:
        outbreak_likelihood = self._outbreak_likelihood(
            population_pressure,
            stage,
        )

        return PestState(
            id=f"pest_state_{pest_profile.id}_{simulation_date.isoformat()}",
            timestamp=climate_state.timestamp,
            source=climate_state.source,
            confidence=confidence,
            pest_id=pest_profile.id,
            current_stage=stage.name,
            accumulated_gdd=accumulated_gdd,
            stage_progression_percentage=self._stage_progress(
                pest_profile,
                stage,
                accumulated_gdd,
            ),
            population_pressure=population_pressure,
            outbreak_likelihood=outbreak_likelihood,
            outbreak_status=self._outbreak_status(
                outbreak_likelihood
            ),
            trend_state=Trend(
                direction=population_pressure.trend,
                acceleration=population_pressure.growth_rate,
                persistence_days=1,
                volatility=0.0,
            ),
            biological_flags=self._biological_flags(
                pest_profile,
                stage,
            ),
            reasoning=reasoning,
        )

    def _profile_stage(
        self,
        pest_profile: PestProfile,
        stage_name: PestLifecycleStage,
    ) -> LifecycleStageProfile:
        for stage in pest_profile.lifecycle_model:
            if stage.name == stage_name:
                return stage

        return pest_profile.lifecycle_model[0]

    def _stage_for_gdd(
        self,
        pest_profile: PestProfile,
        accumulated_gdd: float,
    ) -> LifecycleStageProfile:
        current = pest_profile.lifecycle_model[0]

        for stage in pest_profile.lifecycle_model:
            if accumulated_gdd >= stage.required_gdd:
                current = stage

        return current

    def _stage_name(self, stage: object) -> str:
        return (
            stage.value
            if hasattr(stage, "value")
            else str(stage)
        )

    def _stage_progress(
        self,
        pest_profile: PestProfile,
        stage: LifecycleStageProfile,
        accumulated_gdd: float,
    ) -> float:
        previous_threshold = 0.0

        for candidate in pest_profile.lifecycle_model:
            if candidate.order == stage.order - 1:
                previous_threshold = candidate.required_gdd
                break

        span = max(
            1.0,
            stage.required_gdd - previous_threshold,
        )

        return max(
            0.0,
            min(
                1.0,
                (accumulated_gdd - previous_threshold) / span,
            ),
        )

    def _population_pressure(
        self,
        previous_state: PestState,
        pest_profile: PestProfile,
        stage: LifecycleStageProfile,
        climate_state: ClimateState,
        crop_state: CropState,
        biological_viability: float,
    ) -> PopulationPressure:
        susceptibility = crop_state.susceptibility_context.get(
            pest_profile.id,
            RiskLevel.LOW,
        )

        susceptibility_modifier = {
            RiskLevel.LOW: 0.0,
            RiskLevel.MODERATE: 0.08,
            RiskLevel.HIGH: 0.16,
            RiskLevel.CRITICAL: 0.24,
            "low": 0.0,
            "moderate": 0.08,
            "high": 0.16,
            "critical": 0.24,
        }.get(susceptibility, 0.0)

        reproduction_modifier = (
            pest_profile.reproduction_model.reproduction_rate
            if stage.reproduction_capability
            else 0.0
        )

        thermal_modifier = self._thermal_growth_modifier(
            pest_profile,
            climate_state,
        )

        growth_rate = max(
            0.0,
            (thermal_modifier * 0.18 * biological_viability)
            + susceptibility_modifier
            + reproduction_modifier
        )

        if biological_viability < 0.5:
            growth_rate *= 0.55

        potential = max(
            0.0,
            min(
                1.0,
                previous_state.population_pressure.outbreak_potential
                + growth_rate
                - self._suppression_penalty(climate_state),
            ),
        )

        level = RiskLevel.LOW
        if potential >= 0.75:
            level = RiskLevel.HIGH
        elif potential >= 0.45:
            level = RiskLevel.MODERATE

        trend = (
            TrendDirection.RISING
            if growth_rate > 0.18
            else TrendDirection.STABLE
        )

        return PopulationPressure(
            level=level,
            growth_rate=growth_rate,
            trend=trend,
            outbreak_potential=potential,
        )

    def _outbreak_likelihood(self, population_pressure, stage):
        return max(
            0.0,
            min(
                1.0,
                (population_pressure.outbreak_potential * 0.65)
                + (stage.economic_damage_weight * 0.25),
            ),
        )

    def _thermal_growth_modifier(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
    ) -> float:
        return self._thermal_response(
            pest_profile,
            climate_state,
        )

    def _thermal_response(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
    ) -> float:
        current = climate_state.current_conditions.temperature_c
        base = pest_profile.thermal_properties.base_temperature
        optimal = pest_profile.thermal_properties.optimal_temperature_range
        upper = pest_profile.thermal_properties.upper_temperature_threshold
        midpoint = (optimal.minimum + optimal.maximum) / 2.0
        width = max(0.0001, optimal.maximum - optimal.minimum)

        if current <= base:
            return 0.0

        if current > upper:
            return max(
                0.0,
                0.45 - ((current - upper) * 0.08),
            )

        if optimal.minimum <= current <= optimal.maximum:
            return 1.0

        return max(
            0.15,
            min(
                1.0,
                1.0 - ((abs(current - midpoint) / width) ** 1.7),
            ),
        )

    def _biological_viability(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        crop_state: CropState,
    ) -> float:
        viability = self._thermal_response(
            pest_profile,
            climate_state,
        )

        humidity = climate_state.current_conditions.humidity
        humidity_range = pest_profile.humidity_preferences.optimal_humidity_range

        if humidity < humidity_range.minimum:
            viability *= max(
                0.35,
                1.0 - ((humidity_range.minimum - humidity) / 50.0),
            )
        elif humidity > humidity_range.maximum:
            viability *= max(
                0.45,
                1.0 - ((humidity - humidity_range.maximum) / 60.0),
            )

        if str(
            crop_state.susceptibility_context.get(
                pest_profile.id,
                RiskLevel.LOW,
            )
        ) == RiskLevel.LOW.value:
            viability *= 0.78

        viability *= 1.0 - self._suppression_penalty(climate_state)

        return max(0.0, min(1.0, viability))

    def _suppression_penalty(
        self,
        climate_state: ClimateState,
    ) -> float:
        events = {
            str(event)
            for event in climate_state.environmental_events
        }

        penalty = 0.05

        if EnvironmentalEventType.HEAVY_RAINFALL.value in events:
            penalty += 0.16

        if EnvironmentalEventType.HEATWAVE.value in events:
            penalty += 0.12

        if EnvironmentalEventType.COLD_STRESS.value in events:
            penalty += 0.18

        if EnvironmentalEventType.DROUGHT.value in events:
            penalty += 0.08

        return min(0.45, penalty)

    def _outbreak_status(self, likelihood: float) -> OutbreakStatus:
        if likelihood >= 0.85:
            return OutbreakStatus.PEAK
        if likelihood >= 0.65:
            return OutbreakStatus.ACTIVE
        if likelihood >= 0.45:
            return OutbreakStatus.DEVELOPING
        if likelihood >= 0.25:
            return OutbreakStatus.EMERGING
        return OutbreakStatus.DORMANT

    def _biological_flags(
        self,
        pest_profile: PestProfile,
        stage: LifecycleStageProfile,
    ) -> list[BiologicalEventType]:
        flags = []

        if (
            pest_profile.reproduction_model.generation_overlap_possible
            and stage.reproduction_capability
        ):
            flags.append(BiologicalEventType.OVERLAPPING_GENERATIONS)

        if stage.reproduction_capability:
            flags.append(BiologicalEventType.REPRODUCTIVE_WINDOW)

        return flags
