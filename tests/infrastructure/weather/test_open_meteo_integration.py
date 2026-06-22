from unittest import TestCase

from app.infrastructure.weather.clients.open_meteo_client import OpenMeteoClient
from app.infrastructure.weather.services.weather_service import WeatherService
from app.infrastructure.repositories.postgres.postgres_weather_repository import (
    PostgreSQLWeatherRepository,
)
from app.shared.value_objects import GeoLocation


class OpenMeteoIntegrationTest(TestCase):
    """
    Real infrastructure integration test.

    Hits:
    - Open-Meteo API
    - DTO validation
    - mapper
    - repository
    - PostgreSQL persistence
    """

    def setUp(self) -> None:
        self.client = OpenMeteoClient()
        self.repo = PostgreSQLWeatherRepository()
        self.service = WeatherService(
            weather_client=self.client,
            weather_repository=self.repo,
        )

        self.location = GeoLocation(
            region="khanpur_tehsil",
            latitude=28.6470,
            longitude=70.6560,
        )

    def test_sync_real_historical_weather(self) -> None:
        observations = self.service.sync_historical_weather(
            location=self.location,
            history_days=30,
        )

        self.assertGreater(len(observations), 0)

        persisted = self.repo.get_observations(
            region="khanpur_tehsil",
            start_date=observations[0].timestamp.date(),
            end_date=observations[-1].timestamp.date(),
        )

        self.assertGreater(len(persisted), 0)

    def test_sync_real_forecast_weather(self) -> None:
        observations = self.service.sync_forecast_weather(
            location=self.location,
            forecast_days=14,
        )

        self.assertGreater(len(observations), 0)

        persisted = self.repo.get_forecast(
            region="khanpur_tehsil",
            forecast_days=14,
        )

        self.assertGreater(len(persisted), 0)