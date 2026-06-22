from __future__ import annotations

from app.domain.shared.value_objects import DegreeDay


class GDDPolicy:
    """
    Degree day scientific calculation policy.
    """

    @staticmethod
    def calculate_simple_average(
        t_min: float,
        t_max: float,
        base_temp: float,
        accumulated: float = 0.0,
    ) -> DegreeDay:
        daily = max(
            0.0,
            ((t_max + t_min) / 2.0) - base_temp,
        )

        return DegreeDay(
            daily_value=daily,
            accumulated_value=accumulated + daily,
            calculation_method="simple_average",
            confidence=0.9,
        )