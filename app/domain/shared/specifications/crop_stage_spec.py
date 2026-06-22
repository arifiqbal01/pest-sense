from __future__ import annotations

from app.domain.shared.enums import CropStageType
from app.domain.shared.specifications.specification import Specification


class CropStageSpecification(Specification[CropStageType]):
    """
    Match specific crop stages.
    """

    def __init__(self, allowed_stages: set[CropStageType]):
        self.allowed_stages = allowed_stages

    def is_satisfied_by(self, crop_stage: CropStageType) -> bool:
        return crop_stage in self.allowed_stages