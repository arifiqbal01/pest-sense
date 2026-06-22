from __future__ import annotations

from app.domain.shared.specifications.specification import Specification
from app.domain.shared.value_objects import TemperatureRange


class OptimalTemperatureSpecification(Specification[float]):
    """
    Temperature lies inside biologically optimal band.
    """

    def __init__(self, optimal_range: TemperatureRange):
        self.optimal_range = optimal_range

    def is_satisfied_by(self, temperature_c: float) -> bool:
        return self.optimal_range.contains(temperature_c)


class HeatStressSpecification(Specification[float]):
    """
    Detect harmful elevated thermal stress.
    """

    def __init__(self, threshold_c: float):
        self.threshold_c = threshold_c

    def is_satisfied_by(self, temperature_c: float) -> bool:
        return temperature_c >= self.threshold_c


class ColdStressSpecification(Specification[float]):
    """
    Detect harmful cold stress.
    """

    def __init__(self, threshold_c: float):
        self.threshold_c = threshold_c

    def is_satisfied_by(self, temperature_c: float) -> bool:
        return temperature_c <= self.threshold_c


class LethalTemperatureSpecification(Specification[float]):
    """
    Detect lethal thermal conditions.
    """

    def __init__(self, lethal_threshold_c: float):
        self.lethal_threshold_c = lethal_threshold_c

    def is_satisfied_by(self, temperature_c: float) -> bool:
        return temperature_c >= self.lethal_threshold_c