from __future__ import annotations


class StageTransitionPolicy:
    """
    Shared lifecycle transition policy.
    """

    @staticmethod
    def should_transition(
        accumulated_gdd: float,
        required_gdd: float,
        stress_penalty: float = 0.0,
    ) -> bool:
        adjusted_requirement = required_gdd * (1.0 + stress_penalty)

        return accumulated_gdd >= adjusted_requirement