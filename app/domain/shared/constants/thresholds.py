"""
Scientific/system thresholds.

MVP defaults only.

Species-specific thresholds belong in profiles,
NOT here.
"""

from __future__ import annotations

# =========================
# HUMIDITY
# =========================

HIGH_HUMIDITY_THRESHOLD = 85.0
VERY_HIGH_HUMIDITY_THRESHOLD = 95.0
LOW_HUMIDITY_THRESHOLD = 30.0

# =========================
# RAINFALL
# =========================

LIGHT_RAIN_MM = 2.0
MODERATE_RAIN_MM = 10.0
HEAVY_RAIN_MM = 25.0
EXTREME_RAIN_MM = 50.0

# =========================
# TEMPERATURE
# =========================

HEAT_STRESS_THRESHOLD_C = 38.0
EXTREME_HEAT_THRESHOLD_C = 42.0

COLD_STRESS_THRESHOLD_C = 10.0
FREEZING_THRESHOLD_C = 0.0

RAPID_TEMP_DROP_THRESHOLD_C = 8.0

# =========================
# STABILITY
# =========================

FAVORABLE_STABILITY_DAYS = 3
STRONG_STABILITY_DAYS = 5

VOLATILITY_HIGH_THRESHOLD = 0.70
VOLATILITY_EXTREME_THRESHOLD = 0.90

# =========================
# CONFIDENCE BANDS
# =========================

VERY_LOW_CONFIDENCE_MAX = 0.20
LOW_CONFIDENCE_MAX = 0.40
MODERATE_CONFIDENCE_MAX = 0.70
MODERATE_HIGH_CONFIDENCE_MAX = 0.85
HIGH_CONFIDENCE_MAX = 0.95

# =========================
# RISK CLASSIFICATION
# =========================

LOW_RISK_MAX = 0.30
MODERATE_RISK_MAX = 0.60
HIGH_RISK_MAX = 0.85

# =========================
# SUITABILITY CLASSIFICATION
# =========================

LOW_SUITABILITY_MAX = 0.30
MODERATE_SUITABILITY_MAX = 0.60
HIGH_SUITABILITY_MAX = 0.85

# =========================
# OUTBREAK MOMENTUM
# =========================

EMERGING_OUTBREAK_THRESHOLD = 0.35
DEVELOPING_OUTBREAK_THRESHOLD = 0.55
ACTIVE_OUTBREAK_THRESHOLD = 0.75
PEAK_OUTBREAK_THRESHOLD = 0.90

# =========================
# VALIDATION
# =========================

FALSE_POSITIVE_ERROR_THRESHOLD = 0.40
FALSE_NEGATIVE_ERROR_THRESHOLD = 0.40
CONFIDENCE_CALIBRATION_DRIFT_THRESHOLD = 0.20