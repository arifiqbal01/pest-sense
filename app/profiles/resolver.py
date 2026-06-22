from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.profiles.contracts import (
    CropProfile,
    PestProfile,
    RegionProfile,
    TreatmentProfile,
)
from app.profiles.registry import ProfileRegistry


class ResolvedAnalysisContext(BaseModel):
    """
    Fully resolved biological analysis dependency bundle.
    """

    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )

    crop: CropProfile
    region: RegionProfile
    pests: List[PestProfile]
    treatments: List[TreatmentProfile]


class ProfileResolver:
    """
    Resolves complete biological analysis context.

    Converts high-level identifiers into concrete typed profiles.
    """

    def __init__(self, registry: ProfileRegistry) -> None:
        self.registry = registry

    def resolve_analysis_context(
        self,
        crop: str,
        region: str,
        pests: Optional[List[str]] = None,
    ) -> ResolvedAnalysisContext:
        """
        Resolve crop + region + pest ecosystem context.

        If pests are omitted, region defaults are used.
        """
        crop_profile = self.registry.get_crop_profile(crop)
        region_profile = self.registry.get_region_profile(region)

        if pests:
            pest_profiles = [
                self.registry.get_pest_profile(pest_identifier)
                for pest_identifier in pests
            ]
        else:
            pest_ids = region_profile.pest_patterns.get(
                "common_pests",
                [],
            )

            pest_profiles = [
                self.registry.get_pest_profile(pest_id)
                for pest_id in pest_ids
            ]

        treatments = self._resolve_treatments(pest_profiles)

        return ResolvedAnalysisContext(
            crop=crop_profile,
            region=region_profile,
            pests=pest_profiles,
            treatments=treatments,
        )

    def resolve_single_pest_context(
        self,
        crop: str,
        region: str,
        pest: str,
    ) -> ResolvedAnalysisContext:
        """
        Convenience resolver for single-pest analysis.
        """
        return self.resolve_analysis_context(
            crop=crop,
            region=region,
            pests=[pest],
        )

    def _resolve_treatments(
        self,
        pest_profiles: List[PestProfile],
    ) -> List[TreatmentProfile]:
        """
        Aggregate unique treatment profiles across resolved pests.
        """
        treatments: List[TreatmentProfile] = []
        seen_ids: set[str] = set()

        for pest in pest_profiles:
            pest_treatments = self.registry.treatment_profiles_for_pest(
                pest.id
            )

            for treatment in pest_treatments:
                if treatment.id in seen_ids:
                    continue

                treatments.append(treatment)
                seen_ids.add(treatment.id)

        return treatments