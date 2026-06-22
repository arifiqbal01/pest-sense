from app.application import CurrentAnalysisWorkflow, ValidationWorkflow
from app.domain.climate import ClimateEngine
from app.domain.crop import CropStateEngine
from app.domain.pest import PestStateEngine
from app.domain.recommendation import RecommendationEngine
from app.domain.risk import RiskEngine
from app.domain.suitability import SuitabilityEngine
from app.domain.validation import ValidationEngine
from app.application.workflows import ForecastSimulationEngine


def bootstrap_application(profile_registry):
    climate = ClimateEngine()
    crop = CropStateEngine()
    pest = PestStateEngine()
    suitability = SuitabilityEngine()
    risk = RiskEngine()
    recommendation = RecommendationEngine()
    validation = ValidationEngine()

    return {
        "current_analysis": CurrentAnalysisWorkflow(
            profile_registry=profile_registry,
            climate_engine=climate,
            crop_engine=crop,
            pest_engine=pest,
            suitability_engine=suitability,
            risk_engine=risk,
            recommendation_engine=recommendation,
        ),
        "forecast": ForecastSimulationEngine(
            profile_registry=profile_registry,
            crop_engine=crop,
            pest_engine=pest,
            suitability_engine=suitability,
            risk_engine=risk,
            recommendation_engine=recommendation,
        ),
        "validation": ValidationWorkflow(
            validation_engine=validation,
        ),
    }