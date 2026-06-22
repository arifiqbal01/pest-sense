from __future__ import annotations

from app.domain.shared.enums import UrgencyLevel


class UrgencyPolicy:
    """
    Shared operational urgency policy.
    """

    @staticmethod
    def classify(
        outbreak_acceleration: float,
        crop_criticality: float,
        window_modifier: float,
    ) -> UrgencyLevel:
        composite = (
            outbreak_acceleration
            + crop_criticality
            + window_modifier
        ) / 3.0

        if composite >= 0.9:
            return UrgencyLevel.IMMEDIATE

        if composite >= 0.7:
            return UrgencyLevel.HIGH

        if composite >= 0.4:
            return UrgencyLevel.MODERATE

        return UrgencyLevel.LOW