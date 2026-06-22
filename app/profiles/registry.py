# app/profiles/registry.py
from __future__ import annotations

from typing import Dict, List

from app.profiles.contracts import (
    BaseProfile,
    CropProfile,
    PestProfile,
    RegionProfile,
    TreatmentProfile,
)


class ProfileRegistry:
    """
    In-memory registry for all biological profile assets.
    """

    def __init__(self) -> None:
        self.pest_profiles: Dict[str, PestProfile] = {}
        self.crop_profiles: Dict[str, CropProfile] = {}
        self.region_profiles: Dict[str, RegionProfile] = {}
        self.treatment_profiles: Dict[str, TreatmentProfile] = {}

    def register(self, profile: BaseProfile) -> None:
        if isinstance(profile, PestProfile):
            self.pest_profiles[profile.id] = profile
            return

        if isinstance(profile, CropProfile):
            self.crop_profiles[profile.id] = profile
            return

        if isinstance(profile, RegionProfile):
            self.region_profiles[profile.id] = profile
            return

        if isinstance(profile, TreatmentProfile):
            self.treatment_profiles[profile.id] = profile
            return

        raise TypeError(
            f"Unsupported profile type: {type(profile).__name__}"
        )

    def get_pest_profile(self, profile_id: str) -> PestProfile:
        try:
            return self.pest_profiles[profile_id]
        except KeyError as exc:
            raise KeyError(
                f"Pest profile not found: {profile_id}"
            ) from exc

    def get_crop_profile(self, profile_id: str) -> CropProfile:
        try:
            return self.crop_profiles[profile_id]
        except KeyError as exc:
            raise KeyError(
                f"Crop profile not found: {profile_id}"
            ) from exc

    def get_region_profile(self, profile_id: str) -> RegionProfile:
        try:
            return self.region_profiles[profile_id]
        except KeyError as exc:
            raise KeyError(
                f"Region profile not found: {profile_id}"
            ) from exc

    def get_treatment_profile(
        self,
        profile_id: str,
    ) -> TreatmentProfile:
        try:
            return self.treatment_profiles[profile_id]
        except KeyError as exc:
            raise KeyError(
                f"Treatment profile not found: {profile_id}"
            ) from exc

    def treatment_profiles_for_pest(
        self,
        pest_id: str,
    ) -> List[TreatmentProfile]:
        return [
            profile
            for profile in self.treatment_profiles.values()
            if pest_id in profile.target_pests
        ]

    def has_pest_profile(self, profile_id: str) -> bool:
        return profile_id in self.pest_profiles

    def has_crop_profile(self, profile_id: str) -> bool:
        return profile_id in self.crop_profiles

    def has_region_profile(self, profile_id: str) -> bool:
        return profile_id in self.region_profiles

    def has_treatment_profile(self, profile_id: str) -> bool:
        return profile_id in self.treatment_profiles