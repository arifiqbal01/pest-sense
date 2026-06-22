from __future__ import annotations

from app.domain.shared.specifications.specification import Specification
from app.domain.shared.value_objects import Humidity, HumidityPersistenceMetrics


class OptimalHumiditySpecification(Specification[Humidity]):
    """
    Humidity inside biologically preferred band.
    """

    def __init__(self, minimum: float, maximum: float):
        self.minimum = minimum
        self.maximum = maximum

    def is_satisfied_by(self, humidity: Humidity) -> bool:
        return self.minimum <= humidity.percentage <= self.maximum


class SaturationRiskSpecification(Specification[Humidity]):
    """
    Detect saturation-level humidity.
    """

    def __init__(self, threshold: float = 85.0):
        self.threshold = threshold

    def is_satisfied_by(self, humidity: Humidity) -> bool:
        return humidity.percentage >= self.threshold


class HumidityPersistenceSpecification(
    Specification[HumidityPersistenceMetrics]
):
    """
    Detect prolonged humidity persistence.
    """

    def __init__(self, minimum_humid_hours: int):
        self.minimum_humid_hours = minimum_humid_hours

    def is_satisfied_by(
        self,
        metrics: HumidityPersistenceMetrics,
    ) -> bool:
        return metrics.humid_hours_72h >= self.minimum_humid_hours