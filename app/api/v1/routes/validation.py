from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_validation_workflow
from app.api.v1.contracts.validation import (
    ValidationRequest,
    ValidationResponse,
)
from app.domain.validation import (
    FieldObservation,
    PredictionSnapshot,
)
from app.shared.enums import CropStageType, PestLifecycleStage, RiskLevel
from app.shared.value_objects import GeoLocation

router = APIRouter(
    prefix="/validation",
    tags=["validation"],
)


@router.post(
    "/compare",
    response_model=ValidationResponse,
)
def compare_validation(
    request: ValidationRequest,
    workflow=Depends(get_validation_workflow),
):
    prediction = PredictionSnapshot(
        prediction_id=request.prediction_id,
        timestamp=request.observation_timestamp,
        region=request.region,
        crop_id=request.crop_id,
        pest_id=request.pest_id,
        predicted_stage=PestLifecycleStage(request.predicted_stage),
        predicted_risk=RiskLevel(request.predicted_risk),
        predicted_risk_score=request.predicted_risk_score,
        predicted_outbreak_probability=request.predicted_outbreak_probability,
        prediction_confidence=request.prediction_confidence,
    )

    observation = FieldObservation(
        observation_id="manual_validation",
        timestamp=request.observation_timestamp,
        location=GeoLocation(region=request.region),
        crop_stage=CropStageType(request.observed_crop_stage),
        observed_pest_stage=(
            PestLifecycleStage(request.observed_pest_stage)
            if request.observed_pest_stage
            else None
        ),
        observed_population_pressure=request.observed_population_pressure,
        observed_damage_level=request.observed_damage_level,
        actual_outbreak=request.actual_outbreak,
        observer_confidence=request.observer_confidence,
    )

    result = workflow.run(
        prediction=prediction,
        observation=observation,
    )

    return ValidationResponse(
        validation_id=result.validation_id,
        prediction_id=result.prediction_id,
        pest_id=result.pest_id,
        prediction_accuracy=result.prediction_accuracy,
        risk_accuracy=result.risk_accuracy,
        stage_accuracy=result.stage_accuracy,
        outbreak_timing_accuracy=result.outbreak_timing_accuracy,
        false_positive=result.false_positive,
        false_negative=result.false_negative,
        confidence_accuracy=result.confidence_accuracy,
        calibration_gap=result.calibration_gap,
        validation_notes=result.validation_notes,
    )