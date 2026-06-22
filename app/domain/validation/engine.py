from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import uuid4

from app.domain.validation.models import (
    CalibrationSuggestion,
    ConfidenceAdjustment,
    FieldObservation,
    LearningInsight,
    OutcomeRecord,
    PredictionSnapshot,
    ValidationResult,
)
from app.domain.shared.enums import PestLifecycleStage, RiskLevel, SeverityLevel
from app.domain.shared.contracts import PestState, Recommendation, RiskState
from app.domain.shared.value_objects import TimeWindow, clamp_score


class RuleBasedValidationStrategy:
    risk_order = {
        RiskLevel.LOW.value: 0,
        RiskLevel.MODERATE.value: 1,
        RiskLevel.HIGH.value: 2,
        RiskLevel.CRITICAL.value: 3,
    }

    lifecycle_order = {
        PestLifecycleStage.EGG.value: 0,
        PestLifecycleStage.CRAWLER.value: 1,
        PestLifecycleStage.NYMPH.value: 1,
        PestLifecycleStage.NYMPH_1.value: 1,
        PestLifecycleStage.NYMPH_2.value: 2,
        PestLifecycleStage.NYMPH_3.value: 3,
        PestLifecycleStage.NYMPH_4.value: 4,
        PestLifecycleStage.LARVA.value: 1,
        PestLifecycleStage.PREPUPA.value: 2,
        PestLifecycleStage.PUPA.value: 3,
        PestLifecycleStage.ADULT.value: 4,
        PestLifecycleStage.ADULT_FEMALE.value: 4,
        PestLifecycleStage.ADULT_MALE.value: 4,
        PestLifecycleStage.ADULT_APTEROUS_FEMALE.value: 4,
        PestLifecycleStage.ADULT_ALATE_FEMALE.value: 4,
    }

    observed_level_order = {
        "none": 0,
        "low": 0,
        "minor": 0,
        "moderate": 1,
        "medium": 1,
        "high": 2,
        "severe": 2,
        "critical": 3,
        "extreme": 3,
        "unknown": 1,
    }

    def evaluate(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
        outcome: Optional[OutcomeRecord] = None,
    ) -> ValidationResult:
        risk_accuracy = self.compare_risk_accuracy(prediction, observation)
        stage_accuracy = self.compare_stage_accuracy(prediction, observation)
        timing_accuracy = self.compare_outbreak_timing(
            prediction.expected_peak_window,
            observation,
        )

        false_positive = self.detect_false_positive(
            prediction,
            observation,
        )

        false_negative = self.detect_false_negative(
            prediction,
            observation,
        )

        prediction_accuracy = clamp_score(
            (risk_accuracy * 0.45)
            + (stage_accuracy * 0.35)
            + (timing_accuracy * 0.20)
        )

        confidence_accuracy = clamp_score(
            1.0 - abs(
                prediction.prediction_confidence
                - prediction_accuracy
            )
        )

        calibration_gap = abs(
            prediction.prediction_confidence
            - prediction_accuracy
        )

        confidence_adjustment = self.suggest_confidence_adjustment(
            prediction.prediction_confidence,
            prediction_accuracy,
            observation,
        )

        suggestions = self.generate_calibration_suggestions(
            prediction,
            observation,
            stage_accuracy,
            timing_accuracy,
            false_positive,
            false_negative,
        )

        insights = self.generate_learning_insights(
            prediction,
            observation,
            outcome,
            risk_accuracy,
            stage_accuracy,
            timing_accuracy,
            false_positive,
            false_negative,
        )

        return ValidationResult(
            validation_id=f"validation_{uuid4().hex}",
            prediction_id=prediction.prediction_id,
            observation_id=observation.observation_id,
            pest_id=prediction.pest_id,
            prediction_accuracy=prediction_accuracy,
            risk_accuracy=risk_accuracy,
            stage_accuracy=stage_accuracy,
            outbreak_timing_accuracy=timing_accuracy,
            false_positive=false_positive,
            false_negative=false_negative,
            confidence_accuracy=confidence_accuracy,
            calibration_gap=calibration_gap,
            confidence_adjustment=confidence_adjustment,
            calibration_suggestions=suggestions,
            learning_insights=insights,
            validation_notes=self.validation_notes(
                risk_accuracy,
                stage_accuracy,
                timing_accuracy,
                false_positive,
                false_negative,
            ),
        )

    def compare_stage_accuracy(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
    ) -> float:
        if observation.observed_pest_stage is None:
            return 0.5

        predicted = str(prediction.predicted_stage)
        observed = str(observation.observed_pest_stage)

        if predicted == observed:
            return observation.observer_confidence

        predicted_order = self.lifecycle_order.get(predicted)
        observed_order = self.lifecycle_order.get(observed)

        if predicted_order is None or observed_order is None:
            return 0.25 * observation.observer_confidence

        distance = abs(predicted_order - observed_order)

        if distance == 1:
            return 0.6 * observation.observer_confidence

        return clamp_score(
            (0.2 / max(1, distance))
            * observation.observer_confidence
        )

    def compare_risk_accuracy(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
    ) -> float:
        predicted_rank = self.risk_order[str(prediction.predicted_risk)]
        observed_rank = self.observed_risk_rank(observation)

        distance = abs(predicted_rank - observed_rank)

        ranked_accuracy = max(
            0.0,
            1.0 - (distance / 3.0),
        )

        probability_accuracy = 1.0 - abs(
            prediction.predicted_outbreak_probability
            - self.observed_outbreak_probability(observation)
        )

        return clamp_score(
            (
                (ranked_accuracy * 0.7)
                + (probability_accuracy * 0.3)
            )
            * observation.observer_confidence
        )

    def compare_outbreak_timing(
        self,
        expected_peak_window: Optional[TimeWindow],
        observation: FieldObservation,
    ) -> float:
        observed_date = (
            observation.actual_outbreak_date
            or (
                observation.timestamp.date()
                if observation.actual_outbreak
                else None
            )
        )

        if expected_peak_window is None and observed_date is None:
            return observation.observer_confidence

        if expected_peak_window is None or observed_date is None:
            return 0.25 * observation.observer_confidence

        if expected_peak_window.start <= observed_date <= expected_peak_window.end:
            return observation.observer_confidence

        distance = self.distance_from_window(
            observed_date,
            expected_peak_window,
        )

        return clamp_score(
            (
                1.0 - min(distance, 7) / 7.0
            )
            * observation.observer_confidence
        )

    def detect_false_positive(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
    ) -> bool:
        return self.predicted_outbreak_signal(prediction) and (
            not observation.actual_outbreak
            and self.observed_risk_rank(observation) <= 1
        )

    def detect_false_negative(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
    ) -> bool:
        return (not self.predicted_outbreak_signal(prediction)) and (
            observation.actual_outbreak
            or self.observed_risk_rank(observation) >= 2
        )

    def suggest_confidence_adjustment(
        self,
        original_confidence: float,
        prediction_accuracy: float,
        observation: FieldObservation,
    ) -> ConfidenceAdjustment:
        gap = prediction_accuracy - original_confidence

        amount = abs(gap) * 0.35 * (
            0.5 + observation.observer_confidence * 0.5
        )

        if gap >= 0:
            suggested = clamp_score(original_confidence + amount)
            adjustment = amount
            direction = "increased"
        else:
            suggested = clamp_score(original_confidence - amount)
            adjustment = -amount
            direction = "reduced"

        return ConfidenceAdjustment(
            original_confidence=original_confidence,
            suggested_confidence=suggested,
            adjustment=adjustment,
            reasoning=[
                f"Confidence {direction} because validation accuracy was {prediction_accuracy:.2f}.",
                "Validation suggests calibration only.",
            ],
        )

    def generate_calibration_suggestions(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
        stage_accuracy: float,
        timing_accuracy: float,
        false_positive: bool,
        false_negative: bool,
    ) -> List[CalibrationSuggestion]:
        suggestions = []

        if stage_accuracy < 0.6:
            suggestions.append(
                CalibrationSuggestion(
                    suggestion_id=f"calibration_{uuid4().hex}",
                    target=f"{prediction.pest_id}.lifecycle_model",
                    suggested_adjustment="review_stage_gdd_thresholds",
                    reason="Observed lifecycle stage diverged.",
                    confidence=observation.observer_confidence,
                )
            )

        if timing_accuracy < 0.5:
            suggestions.append(
                CalibrationSuggestion(
                    suggestion_id=f"calibration_{uuid4().hex}",
                    target=f"{prediction.pest_id}.outbreak_timing",
                    suggested_adjustment="review_peak_window_estimation",
                    reason="Observed timing mismatch.",
                    confidence=observation.observer_confidence,
                )
            )

        return suggestions

    def generate_learning_insights(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
        outcome: Optional[OutcomeRecord],
        risk_accuracy: float,
        stage_accuracy: float,
        timing_accuracy: float,
        false_positive: bool,
        false_negative: bool,
    ) -> List[LearningInsight]:
        insights = []

        if false_positive:
            insights.append(
                LearningInsight(
                    insight_type="false_positive",
                    message="Predicted outbreak exceeded field observation.",
                    severity=SeverityLevel.MODERATE,
                    confidence=observation.observer_confidence,
                    related_entities=[
                        prediction.pest_id,
                        prediction.crop_id,
                        prediction.region,
                    ],
                )
            )

        if false_negative:
            insights.append(
                LearningInsight(
                    insight_type="false_negative",
                    message="Observed outbreak exceeded prediction.",
                    severity=SeverityLevel.SEVERE,
                    confidence=observation.observer_confidence,
                    related_entities=[
                        prediction.pest_id,
                        prediction.crop_id,
                        prediction.region,
                    ],
                )
            )

        if not insights:
            insights.append(
                LearningInsight(
                    insight_type="model_alignment",
                    message="Prediction aligned with field validation.",
                    severity=SeverityLevel.MINOR,
                    confidence=observation.observer_confidence,
                    related_entities=[
                        prediction.pest_id,
                        prediction.crop_id,
                        prediction.region,
                    ],
                )
            )

        return insights

    def validation_notes(
        self,
        risk_accuracy: float,
        stage_accuracy: float,
        timing_accuracy: float,
        false_positive: bool,
        false_negative: bool,
    ) -> List[str]:
        notes = [
            f"Risk accuracy: {risk_accuracy:.2f}",
            f"Stage accuracy: {stage_accuracy:.2f}",
            f"Timing accuracy: {timing_accuracy:.2f}",
        ]

        if false_positive:
            notes.append("False positive detected.")

        if false_negative:
            notes.append("False negative detected.")

        return notes

    def observed_risk_rank(
        self,
        observation: FieldObservation,
    ) -> int:
        population_rank = self.observed_level_order.get(
            observation.observed_population_pressure,
            1,
        )

        damage_rank = self.observed_level_order.get(
            observation.observed_damage_level,
            1,
        )

        outbreak_rank = 2 if observation.actual_outbreak else 0

        return max(
            population_rank,
            damage_rank,
            outbreak_rank,
        )

    def observed_outbreak_probability(
        self,
        observation: FieldObservation,
    ) -> float:
        return {
            0: 0.15,
            1: 0.4,
            2: 0.75,
            3: 0.95,
        }[self.observed_risk_rank(observation)]

    def predicted_outbreak_signal(
        self,
        prediction: PredictionSnapshot,
    ) -> bool:
        return (
            self.risk_order[str(prediction.predicted_risk)] >= 2
            or prediction.predicted_outbreak_probability >= 0.65
        )

    def distance_from_window(
        self,
        observed_date: date,
        expected_peak_window: TimeWindow,
    ) -> int:
        if observed_date < expected_peak_window.start:
            return (
                expected_peak_window.start - observed_date
            ).days

        return (
            observed_date - expected_peak_window.end
        ).days


class ValidationEngine:
    def __init__(
        self,
        strategy: Optional[RuleBasedValidationStrategy] = None,
    ) -> None:
        self.strategy = strategy or RuleBasedValidationStrategy()

    def validate_prediction(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
        outcome: Optional[OutcomeRecord] = None,
    ) -> ValidationResult:
        return self.strategy.evaluate(
            prediction=prediction,
            observation=observation,
            outcome=outcome,
        )

    def build_prediction_record(
        self,
        risk_state: RiskState,
        pest_state: PestState,
        region: str,
        crop_id: str,
        recommendation: Optional[Recommendation] = None,
        model_version: str = "mvp_v1",
    ) -> PredictionSnapshot:
        return PredictionSnapshot(
            prediction_id=risk_state.id,
            timestamp=risk_state.timestamp,
            region=region,
            crop_id=crop_id,
            pest_id=risk_state.pest_id,
            predicted_stage=pest_state.current_stage,
            predicted_risk=risk_state.risk_level,
            predicted_risk_score=risk_state.risk_score,
            predicted_outbreak_probability=risk_state.outbreak_probability,
            expected_peak_window=risk_state.expected_peak_window,
            generated_recommendation_id=(
                recommendation.id if recommendation else None
            ),
            prediction_confidence=min(
                risk_state.confidence,
                pest_state.confidence,
            ),
            model_version=model_version,
        )

    def build_prediction_snapshot(
        self,
        risk_state: RiskState,
        pest_state: PestState,
        region: str,
        crop_id: str,
        recommendation: Optional[Recommendation] = None,
        model_version: str = "mvp_v1",
    ) -> PredictionSnapshot:
        return self.build_prediction_record(
            risk_state=risk_state,
            pest_state=pest_state,
            region=region,
            crop_id=crop_id,
            recommendation=recommendation,
            model_version=model_version,
        )