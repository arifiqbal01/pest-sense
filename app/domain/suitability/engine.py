from __future__ import annotations

from typing import Optional

from app.profiles import PestProfile
from app.domain.shared.contracts import (
    ClimateState,
    CropState,
    EnvironmentalStability,
    PestState,
    SuitabilityState,
)
from app.domain.shared.value_objects import (
    SuitabilityScore,
    clamp_score,
)


class WeightedSuitabilityStrategy:
    method = "weighted_suitability_v1"

    def evaluate(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        crop_state: CropState,
        pest_state: Optional[PestState] = None,
        previous_state: Optional[SuitabilityState] = None,
    ) -> SuitabilityState:
        temperature_score = self._temperature_score(
            pest_profile,
            climate_state,
        )

        humidity_score = self._humidity_score(
            pest_profile,
            climate_state,
        )

        rainfall_score = self._rainfall_score(
            climate_state,
        )

        crop_modifier = self._crop_stage_modifier(
            pest_profile,
            crop_state,
        )

        weights = self._normalized_weights(
            pest_profile,
        )

        weighted = (
            (weights["temperature"] * temperature_score)
            + (weights["humidity"] * humidity_score)
            + (weights["rainfall"] * rainfall_score)
        )

        stability = self._environmental_stability(
            weighted,
            previous_state,
        )

        stability_modifier = (
            1.0 + (stability.persistence_strength * 0.08)
        )

        overall = clamp_score(
            weighted
            * crop_modifier
            * stability_modifier
        )

        contributing, limiting = self._factors(
            pest_profile,
            climate_state,
            crop_state,
            temperature_score,
            humidity_score,
            rainfall_score,
            crop_modifier,
        )

        confidence = min(
            climate_state.confidence,
            crop_state.confidence,
        )

        if climate_state.current_conditions.missing_fields:
            confidence = max(0.0, confidence - 0.1)

        current_date = climate_state.timestamp.date()

        return SuitabilityState(
            id=f"suitability_{pest_profile.id}_{current_date.isoformat()}",
            timestamp=climate_state.timestamp,
            source=climate_state.source,
            confidence=confidence,
            pest_id=pest_profile.id,
            score=SuitabilityScore(
                overall_score=overall,
                temperature_score=temperature_score,
                humidity_score=humidity_score,
                rainfall_score=rainfall_score,
                crop_stage_modifier=crop_modifier,
                stability_modifier=stability_modifier,
            ),
            environmental_stability=stability,
            contributing_factors=contributing,
            limiting_factors=limiting,
            evaluation_method=self.method,
        )

    def _temperature_score(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
    ) -> float:
        current = climate_state.current_conditions.temperature_c

        optimal = (
            pest_profile
            .thermal_properties
            .optimal_temperature_range
        )

        upper = (
            pest_profile
            .thermal_properties
            .upper_temperature_threshold
        )

        if current > upper:
            return clamp_score(
                0.45 - ((current - upper) * 0.08)
            )

        midpoint = self._range_midpoint(optimal)

        return clamp_score(
            1.0
            - abs(current - midpoint)
            / self._range_width(optimal)
        )

    def _humidity_score(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
    ) -> float:
        current = climate_state.current_conditions.humidity

        optimal = (
            pest_profile
            .humidity_preferences
            .optimal_humidity_range
        )

        midpoint = self._range_midpoint(optimal)

        return clamp_score(
            1.0
            - abs(current - midpoint)
            / self._range_width(optimal)
        )

    def _rainfall_score(
        self,
        climate_state: ClimateState,
    ) -> float:
        rainfall = (
            climate_state
            .current_conditions
            .rainfall_mm
        )

        if rainfall >= 25:
            return 0.25

        if rainfall >= 5:
            return 0.65

        return 0.9

    def _crop_stage_modifier(
        self,
        pest_profile: PestProfile,
        crop_state: CropState,
    ) -> float:
        crop_key = (
            "cotton"
            if crop_state.crop_id == "crop_cotton"
            else crop_state.crop_id
        )

        stage_key = str(
            crop_state.current_stage
        )

        return (
            pest_profile
            .crop_stage_modifiers
            .get(crop_key, {})
            .get(stage_key, 1.0)
        )

    def _normalized_weights(
        self,
        pest_profile: PestProfile,
    ) -> dict[str, float]:
        raw = pest_profile.suitability_weights

        total = (
            raw.temperature
            + raw.humidity
            + raw.rainfall
        )

        if total <= 0:
            return {
                "temperature": 0.5,
                "humidity": 0.3,
                "rainfall": 0.2,
            }

        return {
            "temperature": raw.temperature / total,
            "humidity": raw.humidity / total,
            "rainfall": raw.rainfall / total,
        }

    def _range_midpoint(
        self,
        value_range,
    ) -> float:
        return (
            value_range.minimum
            + value_range.maximum
        ) / 2.0

    def _range_width(
        self,
        value_range,
    ) -> float:
        return max(
            0.0001,
            value_range.maximum
            - value_range.minimum,
        )

    def _environmental_stability(
        self,
        weighted_score: float,
        previous_state: Optional[SuitabilityState],
    ) -> EnvironmentalStability:
        previous_favorable = 0
        previous_unfavorable = 0
        previous_score = 0.0

        if previous_state:
            previous_favorable = (
                previous_state
                .environmental_stability
                .stable_favorable_days
            )

            previous_unfavorable = (
                previous_state
                .environmental_stability
                .stable_unfavorable_days
            )

            previous_score = (
                previous_state
                .overall_suitability
            )

        if weighted_score >= 0.65:
            favorable = previous_favorable + 1
            unfavorable = 0
        else:
            favorable = 0
            unfavorable = previous_unfavorable + 1

        return EnvironmentalStability(
            stable_favorable_days=favorable,
            stable_unfavorable_days=unfavorable,
            volatility_score=(
                0.0
                if not previous_state
                else abs(weighted_score - previous_score)
            ),
            persistence_strength=clamp_score(
                favorable / 5.0
            ),
        )

    def _factors(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        crop_state: CropState,
        temperature_score: float,
        humidity_score: float,
        rainfall_score: float,
        crop_modifier: float,
    ) -> tuple[list[str], list[str]]:
        contributing: list[str] = []
        limiting: list[str] = []

        if temperature_score >= 0.75:
            contributing.append(
                "Temperature is near pest optimum."
            )
        elif temperature_score <= 0.35:
            limiting.append(
                "Temperature is outside preferred biological range."
            )

        if humidity_score >= 0.70:
            contributing.append(
                "Humidity is favorable."
            )
        elif humidity_score <= 0.35:
            limiting.append(
                "Humidity is limiting suitability."
            )

        if rainfall_score <= 0.40:
            limiting.append(
                "Heavy rainfall may suppress pest activity."
            )

        if crop_modifier > 1.0:
            contributing.append(
                f"Crop stage {crop_state.current_stage} increases favorability."
            )

        return contributing, limiting


class SuitabilityEngine:
    def __init__(
        self,
        strategy: Optional[
            WeightedSuitabilityStrategy
        ] = None,
    ) -> None:
        self.strategy = (
            strategy
            or WeightedSuitabilityStrategy()
        )

    def evaluate(
        self,
        pest_profile: PestProfile,
        climate_state: ClimateState,
        crop_state: CropState,
        pest_state: Optional[PestState] = None,
        previous_state: Optional[SuitabilityState] = None,
    ) -> SuitabilityState:
        return self.strategy.evaluate(
            pest_profile=pest_profile,
            climate_state=climate_state,
            crop_state=crop_state,
            pest_state=pest_state,
            previous_state=previous_state,
        )