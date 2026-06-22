from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject
from app.domain.shared.utils.scoring import clamp_score


class Humidity(ValueObject):
    """
    Atomic relative humidity measurement.

    Represents a single atmospheric relative humidity observation.

    Temporal persistence analysis belongs to climate intelligence,
    not this value object.
    """

    percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Relative humidity percentage.",
    )

    def saturation_risk(self, threshold: float = 85.0) -> float:
        """
        Estimate normalized saturation likelihood for a single reading.

        This is NOT persistence analysis.
        """
        return clamp_score(
            (self.percentage - threshold) / (100.0 - threshold)
        )

    @property
    def is_high(self) -> bool:
        return self.percentage >= 80.0

    @property
    def is_saturating(self) -> bool:
        return self.percentage >= 95.0