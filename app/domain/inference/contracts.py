from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.enums import CropStageType, PestLifecycleStage
from app.domain.shared.contracts import CropState, PestState


class InferenceModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )


class SeasonalWindow(InferenceModel):
    start_mm_dd: str
    end_mm_dd: str


class SeasonalAssumptions(InferenceModel):
    cotton_sowing_window: Optional[SeasonalWindow] = None
    cotton_establishment_window: Optional[SeasonalWindow] = None
    vegetative_growth_window: Optional[SeasonalWindow] = None
    flowering_window: Optional[SeasonalWindow] = None
    boll_formation_window: Optional[SeasonalWindow] = None
    harvest_window: Optional[SeasonalWindow] = None
    primary_pest_risk_window: Optional[SeasonalWindow] = None


class RegionalCropInference(InferenceModel):
    """
    Region-level inferred crop biological assumptions.
    """

    inferred_stage: CropStageType
    estimated_age_days: int = Field(
        ge=0,
    )
    confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )
    reasoning: List[str] = Field(default_factory=list)


class RegionalPestInference(InferenceModel):
    """
    Region-level inferred pest biological assumptions.
    """

    pest_id: str
    inferred_stage: PestLifecycleStage
    outbreak_potential: float = Field(
        ge=0.0,
        le=1.0,
    )
    confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )
    reasoning: List[str] = Field(default_factory=list)


class InferredCurrentState(InferenceModel):
    """
    Final region-aware biological current-state inference.
    """

    crop_state: CropState
    pest_states: List[PestState]

    crop_inference: RegionalCropInference
    pest_inferences: List[RegionalPestInference]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    assumptions: List[str] = Field(default_factory=list)