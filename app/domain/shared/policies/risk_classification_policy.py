from __future__ import annotations

from app.domain.shared.enums import RiskLevel


class RiskClassificationPolicy:
    """
    Shared risk classification policy.
    """

    @staticmethod
    def classify(score: float) -> RiskLevel:
        if score < 0.25:
            return RiskLevel.LOW

        if score < 0.5:
            return RiskLevel.MODERATE

        if score < 0.8:
            return RiskLevel.HIGH

        return RiskLevel.CRITICAL