from __future__ import annotations

from app.domain.shared.value_objects import ConfidenceScore


class ConfidencePolicy:
    """
    Shared confidence evaluation policy.
    """

    @staticmethod
    def evaluate(
        base_confidence: float,
        penalties: list[float] | None = None,
    ) -> ConfidenceScore:
        score = base_confidence

        for penalty in penalties or []:
            score -= penalty

        return ConfidenceScore.from_value(score)