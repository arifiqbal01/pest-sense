"""
Default domain values for PestSense.

These are conservative fallback assumptions,
NOT species-specific biological truths.
"""

from __future__ import annotations

# =========================
# CONFIDENCE DEFAULTS
# =========================

DEFAULT_CONFIDENCE = 0.70
HIGH_CONFIDENCE = 0.85
LOW_CONFIDENCE = 0.40
MIN_CONFIDENCE = 0.10

# =========================
# SCORING DEFAULTS
# =========================

DEFAULT_SCORE = 0.50
MIN_SCORE = 0.0
MAX_SCORE = 1.0

# =========================
# ENVIRONMENTAL WINDOWS
# =========================

DEFAULT_ROLLING_WINDOW_HOURS = 72
DEFAULT_SHORT_WINDOW_HOURS = 24
DEFAULT_WEEK_WINDOW_DAYS = 7

# =========================
# FORECAST
# =========================

DEFAULT_FORECAST_HORIZON_DAYS = 7
MAX_FORECAST_HORIZON_DAYS = 14

# =========================
# CLIMATE
# =========================

DEFAULT_TEMPERATURE_UNIT = "celsius"
DEFAULT_RAINFALL_UNIT = "mm"

# =========================
# SIMULATION
# =========================

DEFAULT_SIMULATION_SOURCE = "current"
DEFAULT_MODEL_VERSION = "1.0"

# =========================
# RISK WEIGHTS (MVP)
# =========================

DEFAULT_BIOLOGICAL_RISK_WEIGHT = 0.35
DEFAULT_ENVIRONMENTAL_RISK_WEIGHT = 0.25
DEFAULT_TREND_RISK_WEIGHT = 0.20
DEFAULT_CROP_VULNERABILITY_WEIGHT = 0.20

# =========================
# SUITABILITY WEIGHTS (FALLBACK)
# =========================

DEFAULT_TEMPERATURE_WEIGHT = 0.50
DEFAULT_HUMIDITY_WEIGHT = 0.30
DEFAULT_RAINFALL_WEIGHT = 0.20

# =========================
# EVENT HISTORY
# =========================

DEFAULT_EVENT_RETENTION_DAYS = 30
DEFAULT_ANOMALY_RETENTION_DAYS = 30

# =========================
# VALIDATION
# =========================

DEFAULT_VALIDATION_LOOKBACK_DAYS = 14
DEFAULT_CALIBRATION_WINDOW_DAYS = 90