from __future__ import annotations


def clamp_score(value: float) -> float:
    """
    Clamp a numeric score into the normalized scientific range [0.0, 1.0].

    Used for:
    - confidence scores
    - suitability scores
    - risk scores
    - outbreak probabilities
    - normalized biological modifiers
    """
    return max(0.0, min(1.0, value))