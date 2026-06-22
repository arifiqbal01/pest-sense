from __future__ import annotations

from app.core.settings import settings
from app.profiles import (
    ProfileResolver,
    load_default_profiles,
)

from app.domain.climate import ClimateEngine
from app.domain.crop import CropStateEngine
from app.domain.pest import PestStateEngine
from app.domain.suitability import SuitabilityEngine
from app.domain.risk import RiskEngine
from app.domain.recommendation import RecommendationEngine
from app.domain.validation import ValidationEngine

from app.application import (
    CurrentAnalysisWorkflow,
    ValidationWorkflow,
)
from app.application.workflows.forecast_engine import ForecastSimulationEngine

from app.infrastructure.weather.clients.open_meteo_client import OpenMeteoClient
from app.infrastructure.weather.services.weather_service import WeatherService
from app.infrastructure.weather.query.weather_query_service import WeatherQueryService
from app.infrastructure.repositories.postgres.postgres_weather_repository import (
    PostgreSQLWeatherRepository,
)


class ApplicationContainer:
    def __init__(self) -> None:
        self.settings = settings

        # profiles
        self.profile_registry = load_default_profiles()

        self.profile_resolver = ProfileResolver(
            registry=self.profile_registry,
        )

        # infrastructure
        self.weather_repository = PostgreSQLWeatherRepository()

        self.weather_client = OpenMeteoClient(
            timeout_seconds=self.settings.HTTP_TIMEOUT_SECONDS,
        )

        self.weather_service = WeatherService(
            weather_client=self.weather_client,
            weather_repository=self.weather_repository,
        )

        self.weather_query_service = WeatherQueryService(
            weather_service=self.weather_service,
        )

        # domain
        self.climate_engine = ClimateEngine()
        self.crop_engine = CropStateEngine()
        self.pest_engine = PestStateEngine()
        self.suitability_engine = SuitabilityEngine()
        self.risk_engine = RiskEngine()
        self.recommendation_engine = RecommendationEngine()
        self.validation_engine = ValidationEngine()

        # workflows
        self.current_analysis_workflow = CurrentAnalysisWorkflow(
            profile_registry=self.profile_registry,
            climate_engine=self.climate_engine,
            suitability_engine=self.suitability_engine,
            risk_engine=self.risk_engine,
            recommendation_engine=self.recommendation_engine,
        )

        self.forecast_simulation_workflow = ForecastSimulationEngine(
            profile_registry=self.profile_registry,
            crop_engine=self.crop_engine,
            pest_engine=self.pest_engine,
            suitability_engine=self.suitability_engine,
            risk_engine=self.risk_engine,
            recommendation_engine=self.recommendation_engine,
        )

        self.validation_workflow = ValidationWorkflow(
            validation_engine=self.validation_engine,
        )


container = ApplicationContainer()