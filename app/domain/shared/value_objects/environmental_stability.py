from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class EnvironmentalStability(ValueObject):
    """
    Temporal environmental persistence descriptor.

    Persistent favorable conditions often drive outbreak acceleration
    more than isolated environmental snapshots.
    """

    stable_favorable_days: int = Field(
        default=0,
        ge=0,
    )

    stable_unfavorable_days: int = Field(
        default=0,
        ge=0,
    )

    volatility_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    persistence_strength: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )