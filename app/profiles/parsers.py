from __future__ import annotations

from app.profiles.contracts import (
    CropProfile,
    PestProfile,
    RegionProfile,
    TreatmentProfile,
)


class ProfileParser:
    """
    Converts raw JSON dictionaries into typed profile contracts.
    """

    @staticmethod
    def parse_crop(data: dict) -> CropProfile:
        return CropProfile.model_validate(data)

    @staticmethod
    def parse_pest(data: dict) -> PestProfile:
        return PestProfile.model_validate(data)

    @staticmethod
    def parse_region(data: dict) -> RegionProfile:
        return RegionProfile.model_validate(data)

    @staticmethod
    def parse_treatment(data: dict) -> TreatmentProfile:
        return TreatmentProfile.model_validate(data)