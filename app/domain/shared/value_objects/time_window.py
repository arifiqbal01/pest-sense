from __future__ import annotations

from datetime import date, datetime

from pydantic import Field, model_validator

from app.domain.shared.base.value_object import ValueObject


class TimeWindow(ValueObject):
    """
    Immutable temporal operational/planning window.

    Used for:
    - intervention timing
    - outbreak peak estimates
    - forecast windows
    - biological opportunity windows
    """

    start: date | datetime
    end: date | datetime

    urgency_modifier: float = Field(
        default=1.0,
        ge=0.0,
        description="Relative urgency multiplier for operational logic.",
    )

    @model_validator(mode="after")
    def validate_window(self) -> "TimeWindow":
        if self.end < self.start:
            raise ValueError(
                "Time window end must be on or after start."
            )
        return self

    @property
    def duration_days(self) -> int:
        """
        Inclusive duration in days.
        """
        if isinstance(self.start, datetime) and isinstance(self.end, datetime):
            return max(1, (self.end.date() - self.start.date()).days + 1)

        if isinstance(self.start, date) and isinstance(self.end, date):
            return (self.end - self.start).days + 1

        raise ValueError(
            "TimeWindow start/end must both be date or both datetime."
        )

    @property
    def is_immediate(self) -> bool:
        return self.urgency_modifier >= 1.5