from app.domain.shared.base.enum import PestSenseEnum


class RiskLevel(PestSenseEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class UrgencyLevel(PestSenseEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    IMMEDIATE = "immediate"


class ConfidenceLevel(PestSenseEnum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    MODERATE_HIGH = "moderate_high"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TrendDirection(PestSenseEnum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class SeverityLevel(PestSenseEnum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class SimulationMode(PestSenseEnum):
    CURRENT = "current"
    FORECAST = "forecast"