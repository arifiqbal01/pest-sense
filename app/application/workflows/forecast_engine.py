from __future__ import annotations

from typing import Dict, List, Optional

from app.domain.crop import CropStateEngine
from app.domain.pest import PestStateEngine
from app.domain.recommendation import RecommendationEngine
from app.domain.risk import RiskEngine
from app.domain.suitability import SuitabilityEngine
from app.profiles import CropProfile, PestProfile, ProfileRegistry
from app.shared.enums import RiskLevel, SimulationMode
from app.shared.kernel import (
    BiologicalForecastTimeline,
    ClimateForecastTimeline,
    CropState,
    PestState,
    ProjectedDayState,
    Recommendation,
    RiskState,
    SimulationContext,
    SuitabilityState,
)
from app.shared.value_objects import TimeWindow


class ForecastSimulationEngine:
    """
    Biological forecast orchestration.

    Responsibilities:
    - consume projected climate intelligence
    - advance crop state
    - advance pest states
    - evaluate suitability
    - evaluate risk
    - generate recommendations

    This workflow does NOT compute climate.
    Climate intelligence must already be prepared upstream.
    """

    def __init__(
        self,
        profile_registry: ProfileRegistry,
        crop_engine: Optional[CropStateEngine] = None,
        pest_engine: Optional[PestStateEngine] = None,
        suitability_engine: Optional[SuitabilityEngine] = None,
        risk_engine: Optional[RiskEngine] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
    ) -> None:
        self.profile_registry = profile_registry
        self.crop_engine = crop_engine or CropStateEngine()
        self.pest_engine = pest_engine or PestStateEngine()
        self.suitability_engine = suitability_engine or SuitabilityEngine()
        self.risk_engine = risk_engine or RiskEngine()
        self.recommendation_engine = (
            recommendation_engine or RecommendationEngine()
        )

    def run(
        self,
        current_crop_state: CropState,
        current_pest_states: List[PestState],
        climate_forecast: ClimateForecastTimeline,
        crop_profile: CropProfile,
        pest_profiles: List[PestProfile],
    ) -> BiologicalForecastTimeline:
        """
        Run biological forward simulation using projected climate states.
        """

        projected_days: List[ProjectedDayState] = []

        previous_crop_state = current_crop_state

        previous_pest_states: Dict[str, PestState] = {
            pest_state.pest_id: pest_state
            for pest_state in current_pest_states
        }

        previous_suitability_states: Dict[str, SuitabilityState] = {}

        confidence_curve: List[float] = []

        for horizon_day, projected_climate in enumerate(
            climate_forecast.projected_states,
            start=1,
        ):
            confidence_modifier = self.apply_confidence_decay(
                projected_climate.confidence,
                horizon_day,
            )

            context = SimulationContext(
                mode=SimulationMode.FORECAST,
                simulation_date=projected_climate.timestamp.date(),
                forecast_horizon_day=horizon_day,
                confidence_modifier=confidence_modifier,
                source=climate_forecast.source,
            )

            projected_crop = self.crop_engine.advance(
                previous_state=previous_crop_state,
                climate_state=projected_climate,
                crop_profile=crop_profile,
                context=context,
            )

            pest_states: List[PestState] = []
            suitability_states: List[SuitabilityState] = []
            risk_states: List[RiskState] = []
            recommendations: List[Recommendation] = []

            for pest_profile in pest_profiles:
                previous_pest = previous_pest_states.get(
                    pest_profile.id
                )

                if previous_pest is None:
                    raise ValueError(
                        f"Missing current pest state for pest: {pest_profile.id}"
                    )

                previous_suitability = previous_suitability_states.get(
                    pest_profile.id
                )

                projected_pest = self.pest_engine.advance(
                    previous_state=previous_pest,
                    pest_profile=pest_profile,
                    climate_state=projected_climate,
                    crop_state=projected_crop,
                    context=context,
                )

                projected_suitability = self.suitability_engine.evaluate(
                    pest_profile=pest_profile,
                    climate_state=projected_climate,
                    crop_state=projected_crop,
                    pest_state=projected_pest,
                    previous_state=previous_suitability,
                )

                projected_risk = self.risk_engine.evaluate(
                    pest_profile=pest_profile,
                    pest_state=projected_pest,
                    crop_state=projected_crop,
                    suitability_state=projected_suitability,
                    climate_state=projected_climate,
                )

                recommendation = self.recommendation_engine.generate(
                    pest_profile=pest_profile,
                    risk_state=projected_risk,
                    pest_state=projected_pest,
                    crop_state=projected_crop,
                    treatment_profiles=(
                        self.profile_registry
                        .treatment_profiles_for_pest(pest_profile.id)
                    ),
                )

                pest_states.append(projected_pest)
                suitability_states.append(projected_suitability)
                risk_states.append(projected_risk)
                recommendations.append(recommendation)

                previous_pest_states[pest_profile.id] = projected_pest
                previous_suitability_states[pest_profile.id] = (
                    projected_suitability
                )

            simulation_confidence = self._calculate_simulation_confidence(
                projected_climate.confidence,
                projected_crop.confidence,
                pest_states,
            )

            confidence_curve.append(simulation_confidence)

            projected_days.append(
                ProjectedDayState(
                    simulation_date=projected_climate.timestamp.date(),
                    projected_climate_state=projected_climate,
                    projected_crop_state=projected_crop,
                    projected_pest_states=pest_states,
                    projected_suitability_states=suitability_states,
                    projected_risk_states=risk_states,
                    projected_recommendations=recommendations,
                    simulation_confidence=simulation_confidence,
                )
            )

            previous_crop_state = projected_crop

        return BiologicalForecastTimeline(
            projected_days=projected_days,
            outbreak_windows=self.detect_outbreak_windows(
                projected_days
            ),
            intervention_windows=self.detect_intervention_windows(
                projected_days
            ),
            confidence_curve=confidence_curve,
            summary=self._summary(projected_days),
        )

    def apply_confidence_decay(
        self,
        climate_confidence: float,
        horizon_day: int,
    ) -> float:
        """
        Forecast uncertainty increases with time horizon.
        """
        decay = (horizon_day - 1) * 0.05

        return max(0.35, climate_confidence - decay)

    def detect_outbreak_windows(
        self,
        projected_days: List[ProjectedDayState],
    ) -> List[TimeWindow]:
        """
        Identify forecast windows containing elevated biological risk.
        """

        windows: List[TimeWindow] = []

        for day in projected_days:
            if any(
                self._is_high_risk(risk.risk_level)
                for risk in day.projected_risk_states
            ):
                windows.append(
                    TimeWindow(
                        start=day.simulation_date,
                        end=day.simulation_date,
                        urgency_modifier=1.0,
                    )
                )

        return windows

    def detect_intervention_windows(
        self,
        projected_days: List[ProjectedDayState],
    ) -> List[TimeWindow]:
        """
        Collect all recommendation timing windows.
        """

        windows: List[TimeWindow] = []

        for day in projected_days:
            for recommendation in day.projected_recommendations:
                if recommendation.timing_window is not None:
                    windows.append(recommendation.timing_window)

        return windows

    def _calculate_simulation_confidence(
        self,
        climate_confidence: float,
        crop_confidence: float,
        pest_states: List[PestState],
    ) -> float:
        """
        Conservative confidence aggregation.
        """

        pest_confidences = [
            pest_state.confidence
            for pest_state in pest_states
        ]

        return min(
            [climate_confidence, crop_confidence] + pest_confidences
        )

    def _summary(
        self,
        projected_days: List[ProjectedDayState],
    ) -> List[str]:
        if not projected_days:
            return ["No projected climate states supplied."]

        high_risk_days = sum(
            1
            for day in projected_days
            if any(
                self._is_high_risk(risk.risk_level)
                for risk in day.projected_risk_states
            )
        )

        return [
            f"Projected {len(projected_days)} biological forecast days.",
            f"High or critical biological risk detected on {high_risk_days} projected days.",
            "Forecast simulation reused crop, pest, suitability, risk, and recommendation engines.",
        ]

    def _is_high_risk(
        self,
        risk_level: object,
    ) -> bool:
        return str(risk_level) in {
            RiskLevel.HIGH.value,
            RiskLevel.CRITICAL.value,
        }