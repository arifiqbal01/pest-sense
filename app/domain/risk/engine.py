from __future__ import annotations

from datetime import timedelta
from typing import Optional

from app.profiles import PestProfile
from app.domain.shared.enums import (
    EnvironmentalEventType,
    RiskLevel,
    SeverityLevel,
    TrendDirection,
    UrgencyLevel,
)
from app.domain.shared.contracts import (
    ClimateState,
    CropState,
    PestState,
    RiskState,
    SuitabilityState,
)
from app.domain.shared.value_objects import (
    TimeWindow,
    clamp_score,
)


class WeightedRiskStrategy:
    method = "weighted_risk_v1"

    def evaluate(
        self,
        pest_profile: PestProfile,
        pest_state: PestState,
        crop_state: CropState,
        suitability_state: SuitabilityState,
        climate_state: Optional[ClimateState] = None,
        intervention_history: Optional[list] = None,
    ) -> RiskState:
        stage_risk = self._stage_risk(
            pest_profile,
            pest_state,
        )

        suitability_risk = (
            suitability_state.overall_suitability
        )

        trend_risk = self._trend_risk(
            pest_state,
            suitability_state,
        )

        crop_risk = self._crop_vulnerability(
            crop_state,
            pest_profile.id,
        )

        suppression = self._suppression_context(
            climate_state,
            intervention_history,
        )

        score = clamp_score(
            (0.32 * stage_risk)
            + (0.30 * suitability_risk)
            + (0.23 * trend_risk)
            + (0.15 * crop_risk)
            - suppression
        )

        risk_level = self._risk_level(score)
        severity = self._severity(score)
        urgency = self._urgency(
            score,
            pest_state,
            crop_risk,
        )

        contributing = self._contributing_factors(
            pest_state,
            crop_state,
            suitability_state,
            crop_risk,
        )

        limiting = list(
            suitability_state.limiting_factors
        )

        confidence = min(
            pest_state.confidence,
            crop_state.confidence,
            suitability_state.confidence,
        )

        expected_peak_window = self._peak_window(
            score,
            pest_state,
            crop_state,
        )

        reasoning = [
            (
                f"Risk combines lifecycle ({stage_risk:.2f}), "
                f"suitability ({suitability_risk:.2f}), "
                f"trend ({trend_risk:.2f}), "
                f"crop vulnerability ({crop_risk:.2f}), "
                f"suppression ({suppression:.2f})."
            )
        ]

        reasoning.extend(contributing[:4])

        current_date = crop_state.timestamp.date()

        return RiskState(
            id=f"risk_{pest_profile.id}_{current_date.isoformat()}",
            timestamp=crop_state.timestamp,
            source=crop_state.source,
            confidence=confidence,
            pest_id=pest_profile.id,
            risk_level=risk_level,
            risk_score=score,
            urgency=urgency,
            severity=severity,
            outbreak_probability=clamp_score(
                (score * 0.65)
                + (
                    pest_state.outbreak_likelihood
                    * 0.35
                )
                - (suppression * 0.25)
            ),
            expected_peak_window=expected_peak_window,
            contributing_factors=contributing,
            limiting_factors=limiting,
            reasoning=reasoning,
            evaluation_method=self.method,
        )

    def _stage_risk(
        self,
        pest_profile: PestProfile,
        pest_state: PestState,
    ) -> float:
        current_stage = str(
            pest_state.current_stage
        )

        for stage in pest_profile.lifecycle_model:
            if str(stage.name) == current_stage:
                return stage.economic_damage_weight

        return 0.3

    def _trend_risk(
        self,
        pest_state: PestState,
        suitability_state: SuitabilityState,
    ) -> float:
        trend_bonus = (
            0.2
            if str(
                pest_state.population_pressure.trend
            )
            == TrendDirection.RISING.value
            else 0.0
        )

        persistence_bonus = min(
            0.2,
            (
                suitability_state
                .environmental_stability
                .stable_favorable_days
                * 0.04
            ),
        )

        return clamp_score(
            pest_state.population_pressure.outbreak_potential
            + trend_bonus
            + persistence_bonus
        )

    def _crop_vulnerability(
        self,
        crop_state: CropState,
        pest_id: str,
    ) -> float:
        susceptibility = (
            crop_state.susceptibility_context.get(
                pest_id,
                RiskLevel.LOW,
            )
        )

        return {
            RiskLevel.LOW: 0.2,
            RiskLevel.MODERATE: 0.5,
            RiskLevel.HIGH: 0.78,
            RiskLevel.CRITICAL: 1.0,
            "low": 0.2,
            "moderate": 0.5,
            "high": 0.78,
            "critical": 1.0,
        }.get(susceptibility, 0.2)

    def _risk_level(
        self,
        score: float,
    ) -> RiskLevel:
        if score >= 0.82:
            return RiskLevel.CRITICAL
        if score >= 0.62:
            return RiskLevel.HIGH
        if score >= 0.35:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    def _severity(
        self,
        score: float,
    ) -> SeverityLevel:
        if score >= 0.82:
            return SeverityLevel.EXTREME
        if score >= 0.62:
            return SeverityLevel.SEVERE
        if score >= 0.35:
            return SeverityLevel.MODERATE
        return SeverityLevel.MINOR

    def _urgency(
        self,
        score: float,
        pest_state: PestState,
        crop_risk: float,
    ) -> UrgencyLevel:
        rising = (
            str(
                pest_state.population_pressure.trend
            )
            == TrendDirection.RISING.value
        )

        if score >= 0.82 or (
            rising and crop_risk >= 0.9
        ):
            return UrgencyLevel.IMMEDIATE

        if score >= 0.62:
            return UrgencyLevel.HIGH

        if score >= 0.35:
            return UrgencyLevel.MODERATE

        return UrgencyLevel.LOW

    def _peak_window(
        self,
        score: float,
        pest_state: PestState,
        crop_state: CropState,
    ) -> Optional[TimeWindow]:
        if score < 0.55:
            return None

        rising = (
            str(
                pest_state.population_pressure.trend
            )
            == TrendDirection.RISING.value
        )

        start = crop_state.timestamp.date() + timedelta(
            days=2 if rising else 4
        )

        end = start + timedelta(days=3)

        return TimeWindow(
            start=start,
            end=end,
            urgency_modifier=max(1.0, score),
        )

    def _suppression_context(
        self,
        climate_state: Optional[ClimateState],
        intervention_history: Optional[list],
    ) -> float:
        suppression = 0.0

        if climate_state is not None:
            events = {
                str(event)
                for event in climate_state.environmental_events
            }

            if EnvironmentalEventType.HEAVY_RAINFALL.value in events:
                suppression += 0.10

            if EnvironmentalEventType.COLD_STRESS.value in events:
                suppression += 0.08

            if EnvironmentalEventType.HEATWAVE.value in events:
                suppression += 0.05

        if intervention_history:
            recent_success = any(
                bool(getattr(item, "outbreak_suppression", False))
                or (
                    isinstance(item, dict)
                    and item.get("outbreak_suppression") is True
                )
                for item in intervention_history[-3:]
            )

            if recent_success:
                suppression += 0.12

        return clamp_score(suppression)

    def _contributing_factors(
        self,
        pest_state: PestState,
        crop_state: CropState,
        suitability_state: SuitabilityState,
        crop_risk: float,
    ) -> list[str]:
        factors = list(
            suitability_state.contributing_factors
        )

        if crop_risk >= 0.75:
            factors.append(
                f"Crop stage {crop_state.current_stage} is highly vulnerable."
            )

        if (
            str(
                pest_state.population_pressure.trend
            )
            == TrendDirection.RISING.value
        ):
            factors.append(
                "Population pressure is rising."
            )

        damaging_stages = {
            "nymph",
            "larva",
            "adult",
            "adult_female",
            "adult_male",
        }

        if str(pest_state.current_stage) in damaging_stages:
            factors.append(
                f"Pest stage {pest_state.current_stage} has meaningful damage potential."
            )

        return factors


class RiskEngine:
    def __init__(
        self,
        strategy: Optional[
            WeightedRiskStrategy
        ] = None,
    ) -> None:
        self.strategy = (
            strategy
            or WeightedRiskStrategy()
        )

    def evaluate(
        self,
        pest_profile: PestProfile,
        pest_state: PestState,
        crop_state: CropState,
        suitability_state: SuitabilityState,
        climate_state: Optional[
            ClimateState
        ] = None,
        intervention_history: Optional[
            list
        ] = None,
    ) -> RiskState:
        return self.strategy.evaluate(
            pest_profile=pest_profile,
            pest_state=pest_state,
            crop_state=crop_state,
            suitability_state=suitability_state,
            climate_state=climate_state,
            intervention_history=intervention_history,
        )
