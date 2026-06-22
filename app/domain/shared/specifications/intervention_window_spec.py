from __future__ import annotations

from datetime import datetime

from app.domain.shared.specifications.specification import Specification
from app.domain.shared.value_objects import TimeWindow


class ActiveInterventionWindowSpecification(Specification[datetime]):
    """
    Determine whether intervention window is currently active.
    """

    def __init__(self, window: TimeWindow):
        self.window = window

    def is_satisfied_by(self, now: datetime) -> bool:
        return self.window.start <= now <= self.window.end