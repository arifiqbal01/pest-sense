from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from .base import ApiModel


class HealthResponse(ApiModel):
    name: str
    status: str
    environment: str