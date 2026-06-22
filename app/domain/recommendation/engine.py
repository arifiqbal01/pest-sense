from __future__ import annotations

from datetime import timedelta
from typing import List, Optional

from app.profiles import PestProfile, TreatmentProfile
from app.domain.shared.enums import (
    InterventionType,
    RiskLevel,
    UrgencyLevel,
)
from app.domain.shared.contracts import (
    CropState,
    PestState,
    Recommendation,
    RiskState,
)
from app.domain.shared.value_objects import TimeWindow, clamp_score


class HeuristicRecommendationStrategy:
    method = "heuristic_recommendation_v1"

    def generate(
        self,
        pest_profile: PestProfile,
        risk_state: RiskState,
        pest_state: PestState,
        crop_state: CropState,
        treatment_profiles: List[TreatmentProfile],
        suitability_state=None,
        intervention_history: Optional[list] = None,
    ) -> Recommendation:
        risk_level = str(risk_state.risk_level)

        scouting = self._scouting_profile(
            treatment_profiles
        )

        if risk_state.confidence < 0.65:
            if scouting is not None:
                return self._scouting_recommendation(
                    treatment=scouting,
                    pest_profile=pest_profile,
                    risk_state=risk_state,
                    pest_state=pest_state,
                    crop_state=crop_state,
                    reason="Prediction confidence requires field verification before intervention.",
                )

        if risk_level in {
            RiskLevel.HIGH.value,
            RiskLevel.CRITICAL.value,
        } and risk_state.risk_score >= 0.62:
            treatment = self._best_treatment(
                pest_state,
                treatment_profiles,
            )

            if treatment is not None and self._environment_allows_intervention(
                risk_state
            ):
                return self._treatment_recommendation(
                    treatment=treatment,
                    pest_profile=pest_profile,
                    risk_state=risk_state,
                    pest_state=pest_state,
                    crop_state=crop_state,
                )

            if scouting is not None:
                return self._scouting_recommendation(
                    treatment=scouting,
                    pest_profile=pest_profile,
                    risk_state=risk_state,
                    pest_state=pest_state,
                    crop_state=crop_state,
                    reason="Risk is elevated, but compatible or operationally safe intervention is not available.",
                )

        if (
            risk_level == RiskLevel.MODERATE.value
            or risk_state.confidence < 0.65
        ):
            if scouting is not None:
                return self._scouting_recommendation(
                    treatment=scouting,
                    pest_profile=pest_profile,
                    risk_state=risk_state,
                    pest_state=pest_state,
                    crop_state=crop_state,
                )

        current_date = crop_state.timestamp.date()

        return Recommendation(
            id=(
                f"recommendation_"
                f"{pest_profile.id}_"
                f"{current_date.isoformat()}"
            ),
            timestamp=crop_state.timestamp,
            source=crop_state.source,
            confidence=risk_state.confidence,
            recommended_action="monitor_conditions",
            intervention_type=InterventionType.MONITOR_ONLY,
            target_pest=pest_profile.id,
            target_stage=pest_state.current_stage,
            urgency=UrgencyLevel.LOW,
            expected_effectiveness=0.0,
            expected_risk_reduction=0.0,
            operational_notes=[
                "Continue routine field observation."
            ],
            reasoning=[
                "Risk remains below intervention threshold."
            ],
            alternative_options=[
                "Scout if pest pressure begins rising."
            ],
        )

    def _best_treatment(
        self,
        pest_state: PestState,
        treatment_profiles: List[TreatmentProfile],
    ) -> Optional[TreatmentProfile]:
        compatible = []

        for treatment in treatment_profiles:
            if (
                treatment.treatment_type
                == InterventionType.SCOUTING
            ):
                continue

            valid_stages = {
                str(stage)
                for stage in treatment.target_lifecycle_stages
            }

            if (
                str(pest_state.current_stage)
                in valid_stages
            ):
                compatible.append(treatment)

        if not compatible:
            return None

        return max(
            compatible,
            key=lambda t: (
                t.effectiveness_model.expected_reduction
            ),
        )

    def _scouting_profile(
        self,
        treatment_profiles: List[TreatmentProfile],
    ) -> Optional[TreatmentProfile]:
        for treatment in treatment_profiles:
            if (
                treatment.treatment_type
                == InterventionType.SCOUTING
            ):
                return treatment

        return None

    def _environment_allows_intervention(
        self,
        risk_state: RiskState,
    ) -> bool:
        limiting = " ".join(
            risk_state.limiting_factors
            + risk_state.reasoning
        ).lower()

        blocked_terms = {
            "heavy rainfall",
            "cold stress",
            "environmental suppression",
        }

        return not any(term in limiting for term in blocked_terms)

    def _treatment_recommendation(
        self,
        treatment: TreatmentProfile,
        pest_profile: PestProfile,
        risk_state: RiskState,
        pest_state: PestState,
        crop_state: CropState,
    ) -> Recommendation:
        start = crop_state.timestamp.date()

        urgent = str(risk_state.urgency) in {
            UrgencyLevel.HIGH.value,
            UrgencyLevel.IMMEDIATE.value,
        }

        end = start + timedelta(
            days=2 if urgent else 4
        )

        expected_effectiveness = (
            treatment.effectiveness_model.expected_reduction
        )

        risk_reduction = clamp_score(
            expected_effectiveness
            * risk_state.risk_score
        )

        return Recommendation(
            id=(
                f"recommendation_"
                f"{pest_profile.id}_"
                f"{start.isoformat()}"
            ),
            timestamp=crop_state.timestamp,
            source=crop_state.source,
            confidence=min(
                risk_state.confidence,
                0.85,
            ),
            recommended_action=treatment.id,
            intervention_type=treatment.treatment_type,
            target_pest=pest_profile.id,
            target_stage=pest_state.current_stage,
            urgency=risk_state.urgency,
            timing_window=TimeWindow(
                start=start,
                end=end,
                urgency_modifier=risk_state.risk_score,
            ),
            expected_effectiveness=expected_effectiveness,
            expected_risk_reduction=risk_reduction,
            operational_notes=[
                "Validate field counts before intervention.",
                "Rotate chemistry if repeated applications occurred.",
            ],
            reasoning=[
                (
                    f"{risk_state.risk_level} risk aligns "
                    f"with vulnerable pest stage "
                    f"{pest_state.current_stage}."
                ),
                (
                    f"Crop stage "
                    f"{crop_state.current_stage} "
                    f"increases intervention importance."
                ),
            ] + risk_state.reasoning[:2],
            alternative_options=[
                "Use focused scouting if intervention conditions are unsuitable."
            ],
        )

    def _scouting_recommendation(
        self,
        treatment: TreatmentProfile,
        pest_profile: PestProfile,
        risk_state: RiskState,
        pest_state: PestState,
        crop_state: CropState,
        reason: str = "Risk or confidence level requires field verification.",
    ) -> Recommendation:
        start = crop_state.timestamp.date()

        urgency = (
            risk_state.urgency
            if str(risk_state.urgency) in {
                UrgencyLevel.HIGH.value,
                UrgencyLevel.IMMEDIATE.value,
            }
            else UrgencyLevel.MODERATE
        )

        return Recommendation(
            id=(
                f"recommendation_"
                f"{pest_profile.id}_"
                f"{start.isoformat()}"
            ),
            timestamp=crop_state.timestamp,
            source=crop_state.source,
            confidence=risk_state.confidence,
            recommended_action=treatment.id,
            intervention_type=InterventionType.SCOUTING,
            target_pest=pest_profile.id,
            target_stage=pest_state.current_stage,
            urgency=urgency,
            timing_window=TimeWindow(
                start=start,
                end=start + timedelta(days=2),
                urgency_modifier=1.0,
            ),
            expected_effectiveness=0.0,
            expected_risk_reduction=0.0,
            operational_notes=[
                "Scout leaf undersides and record lifecycle stage distribution."
            ],
            reasoning=[
                reason,
                (
                    f"Predicted pest stage: "
                    f"{pest_state.current_stage}."
                ),
            ],
            alternative_options=[
                "Continue passive monitoring if counts remain low."
            ],
        )


class RecommendationEngine:
    def __init__(
        self,
        strategy: Optional[
            HeuristicRecommendationStrategy
        ] = None,
    ) -> None:
        self.strategy = (
            strategy
            or HeuristicRecommendationStrategy()
        )

    def generate(
        self,
        pest_profile: PestProfile,
        risk_state: RiskState,
        pest_state: PestState,
        crop_state: CropState,
        treatment_profiles: List[TreatmentProfile],
        suitability_state=None,
        intervention_history: Optional[list] = None,
    ) -> Recommendation:
        return self.strategy.generate(
            pest_profile=pest_profile,
            risk_state=risk_state,
            pest_state=pest_state,
            crop_state=crop_state,
            treatment_profiles=treatment_profiles,
            suitability_state=suitability_state,
            intervention_history=intervention_history,
        )
