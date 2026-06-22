from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject
from app.domain.shared.enums import TrendDirection


class Trend(ValueObject):
    """
    Temporal directional trend descriptor.

    Used for biological, environmental, and operational trend
    interpretation across domain engines.
    """

    direction: TrendDirection

    acceleration: float = Field(
        default=0.0,
        description="Rate of directional change.",
    )

    persistence_days: int = Field(
        default=0,
        ge=0,
        description="Number of consecutive days the trend persisted.",
    )

    volatility: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Normalized instability score.",
    )

    @property
    def is_rising(self) -> bool:
        return self.direction == TrendDirection.RISING

    @property
    def is_falling(self) -> bool:
        return self.direction == TrendDirection.FALLING

    @property
    def is_stable(self) -> bool:
        return self.direction == TrendDirection.STABLE

    @property
    def is_volatile(self) -> bool:
        return self.direction == TrendDirection.VOLATILE