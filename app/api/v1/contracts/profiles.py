from __future__ import annotations

from typing import List
from .base import ApiModel
from pydantic import BaseModel, ConfigDict


class ProfileSummary(ApiModel):
    id: str
    name: str


class PestProfilesResponse(ApiModel):
    items: List[ProfileSummary]


class CropProfilesResponse(ApiModel):
    items: List[ProfileSummary]


class RegionProfilesResponse(ApiModel):
    items: List[ProfileSummary]