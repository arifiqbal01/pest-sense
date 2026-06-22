from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject
from app.domain.shared.enums import EnvironmentalEventType, SeverityLevel


class Anomaly(ValueObject):
    """
    Represents an abnormal environmental condition detected
    by the climate intelligence layer.

    This is environmental truth only—not biological interpretation.
    """

    anomaly_type: EnvironmentalEventType
    severity: SeverityLevel
    detected_at: datetime

    expected_impact: str = Field(
        min_length=1,
        description="Human-readable environmental impact summary.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Detection confidence score.",
    )