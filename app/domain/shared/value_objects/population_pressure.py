from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject
from app.domain.shared.enums import RiskLevel, TrendDirection


class PopulationPressure(ValueObject):
    """
    Biological population pressure descriptor for pest dynamics.

    Represents normalized ecological pressure, not direct field counts.
    """

    level: RiskLevel

    growth_rate: float = Field(
        default=0.0,
        description="Relative biological growth pressure.",
    )

    trend: TrendDirection = Field(
        default=TrendDirection.STABLE,
        description="Observed biological population direction.",
    )

    outbreak_potential: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Normalized outbreak escalation potential.",
    )