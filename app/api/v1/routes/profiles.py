from fastapi import APIRouter, Depends

from app.api.dependencies import get_profile_registry
from app.api.v1.contracts.profiles import (
    CropProfilesResponse,
    PestProfilesResponse,
    ProfileSummary,
    RegionProfilesResponse,
)

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
)


@router.get(
    "/crops",
    response_model=CropProfilesResponse,
)
def crops(
    registry=Depends(get_profile_registry),
):
    return CropProfilesResponse(
        items=[
            ProfileSummary(
                id=profile.id,
                name=profile.name,
            )
            for profile in registry.crop_profiles.values()
        ]
    )


@router.get(
    "/pests",
    response_model=PestProfilesResponse,
)
def pests(
    registry=Depends(get_profile_registry),
):
    return PestProfilesResponse(
        items=[
            ProfileSummary(
                id=profile.id,
                name=profile.name,
            )
            for profile in registry.pest_profiles.values()
        ]
    )


@router.get(
    "/regions",
    response_model=RegionProfilesResponse,
)
def regions(
    registry=Depends(get_profile_registry),
):
    return RegionProfilesResponse(
        items=[
            ProfileSummary(
                id=profile.id,
                name=profile.name,
            )
            for profile in registry.region_profiles.values()
        ]
    )