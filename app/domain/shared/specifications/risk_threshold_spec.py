from __future__ import annotations

from app.domain.shared.specifications.specification import Specification
from app.domain.shared.value_objects import RiskScore


class HighRiskSpecification(Specification[RiskScore]):
    """
    Detect high operational risk.
    """

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    def is_satisfied_by(self, risk: RiskScore) -> bool:
        return risk.value >= self.threshold


class CriticalRiskSpecification(Specification[RiskScore]):
    """
    Detect critical operational danger.
    """

    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold

    def is_satisfied_by(self, risk: RiskScore) -> bool:
        return risk.value >= self.threshold