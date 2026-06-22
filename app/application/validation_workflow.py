from __future__ import annotations

from typing import Optional

from app.domain.validation import FieldObservation, OutcomeRecord, PredictionSnapshot, ValidationEngine, ValidationResult


class ValidationWorkflow:
    """Thin orchestration wrapper for MVP validation comparisons."""

    def __init__(self, validation_engine: Optional[ValidationEngine] = None) -> None:
        self.validation_engine = validation_engine or ValidationEngine()

    def run(
        self,
        prediction: PredictionSnapshot,
        observation: FieldObservation,
        outcome: Optional[OutcomeRecord] = None,
    ) -> ValidationResult:
        return self.validation_engine.validate_prediction(prediction=prediction, observation=observation, outcome=outcome)
