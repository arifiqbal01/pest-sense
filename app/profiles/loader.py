# app/profiles/loader.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Type

from app.profiles.contracts import (
    BaseProfile,
    CropProfile,
    PestProfile,
    RegionProfile,
    TreatmentProfile,
)
from app.profiles.registry import ProfileRegistry


class ProfileLoader:
    """
    Loads JSON biological profiles into an in-memory registry.
    """

    profile_types: Dict[str, Type[BaseProfile]] = {
        "PestProfile": PestProfile,
        "CropProfile": CropProfile,
        "RegionProfile": RegionProfile,
        "TreatmentProfile": TreatmentProfile,
    }

    def __init__(
        self,
        base_path: Optional[Path] = None,
    ) -> None:
        self.base_path = (
            base_path
            or Path(__file__).resolve().parent
        )

    def load_json_profiles(self) -> ProfileRegistry:
        if not self.base_path.exists():
            raise FileNotFoundError(
                f"Profile directory not found: {self.base_path}"
            )

        registry = ProfileRegistry()

        for path in sorted(self.base_path.glob("*/*.json")):
            profile = self.load_profile(path)
            registry.register(profile)

        return registry

    def load_profile(
        self,
        path: Path,
    ) -> BaseProfile:
        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as profile_file:
                data = json.load(profile_file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in profile file: {path}"
            ) from exc

        profile_type = data.get("type")

        if profile_type not in self.profile_types:
            raise ValueError(
                f"Unsupported profile type {profile_type!r} in {path}"
            )

        profile_model = self.profile_types[profile_type]

        return profile_model.model_validate(data)


def load_default_profiles() -> ProfileRegistry:
    """
    Loads bundled default PestSense profiles.
    """
    return ProfileLoader().load_json_profiles()