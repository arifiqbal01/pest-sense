from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

class ApiModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )