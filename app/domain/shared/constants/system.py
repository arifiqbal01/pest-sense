"""
System-level architectural constants for domain only
"""

from __future__ import annotations

# =========================
# ENGINE IDENTIFIERS
# =========================

CLIMATE_ENGINE = "climate_engine"
CROP_ENGINE = "crop_engine"
PEST_ENGINE = "pest_engine"
SUITABILITY_ENGINE = "suitability_engine"
RISK_ENGINE = "risk_engine"
RECOMMENDATION_ENGINE = "recommendation_engine"
VALIDATION_ENGINE = "validation_engine"
INFERENCE_ENGINE = "inference_engine"

# =========================
# EVALUATION METHODS
# =========================

WEIGHTED_SUITABILITY_METHOD = "weighted_suitability_v1"
WEIGHTED_RISK_METHOD = "weighted_risk_v1"
HEURISTIC_RECOMMENDATION_METHOD = "heuristic_recommendation_v1"
RULE_BASED_VALIDATION_METHOD = "rule_based_validation_v1"
