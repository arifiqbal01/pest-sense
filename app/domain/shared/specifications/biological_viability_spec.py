from __future__ import annotations

from app.domain.shared.specifications.specification import Specification
from app.domain.shared.value_objects import TemperatureRange


class BiologicalViabilitySpecification(Specification[float]):
    """
    Determines whether environmental temperature permits survival.
    """

    def __init__(self, viable_range: TemperatureRange):
        self.viable_range = viable_range

    def is_satisfied_by(self, temperature_c: float) -> bool:
        return self.viable_range.contains(temperature_c)


class ReproductiveViabilitySpecification(Specification[float]):
    """
    Determines whether reproduction is biologically feasible.
    """

    def __init__(self, reproductive_range: TemperatureRange):
        self.reproductive_range = reproductive_range

    def is_satisfied_by(self, temperature_c: float) -> bool:
        return self.reproductive_range.contains(temperature_c)