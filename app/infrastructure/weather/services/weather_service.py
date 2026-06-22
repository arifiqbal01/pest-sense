# app/infrastructure/weather/services/weather_service.py
from __future__ import annotations

from datetime import date, timedelta
from typing import List

from app.infrastructure.weather.clients.open_meteo_client import OpenMeteoClient
from app.infrastructure.weather.mappers.weather_mapper import WeatherMapper
from app.infrastructure.weather.repositories.weather_repository import (
    WeatherRepository,
)
from app.shared.kernel import HourlyClimateObservation
from app.shared.value_objects import GeoLocation


class WeatherService:
    """
    Weather orchestration service.

    Responsibilities:
    - coordinate repository/cache
    - fetch external weather data
    - map provider DTOs into domain states
    - persist normalized observations

    NOT responsible for:
    - climate biology calculations
    - GDD
    - suitability
    - risk
    """

    def __init__(
        self,
        weather_client: OpenMeteoClient,
        weather_repository: WeatherRepository,
    ) -> None:
        self._weather_client = weather_client
        self._weather_repository = weather_repository

    def sync_historical_weather(
        self,
        location: GeoLocation,
        history_days: int = 90,
    ) -> list[HourlyClimateObservation]:
        """
        Fetch and persist historical weather observations.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=history_days)

        dto = self._weather_client.get_historical(
            latitude=location.latitude,
            longitude=location.longitude,
            start_date=start_date,
            end_date=end_date,
        )

        observations = WeatherMapper.open_meteo_to_hourly_observations(
            payload=dto,
            region=location.region,
        )

        self._weather_repository.save_observations(observations)

        return observations

    def sync_forecast_weather(
        self,
        location: GeoLocation,
        forecast_days: int = 14,
    ) -> list[HourlyClimateObservation]:
        """
        Fetch and persist forecast weather observations.
        """
        dto = self._weather_client.get_forecast(
            latitude=location.latitude,
            longitude=location.longitude,
            forecast_days=forecast_days,
        )

        observations = WeatherMapper.open_meteo_to_hourly_observations(
            payload=dto,
            region=location.region,
        )

        self._weather_repository.save_forecast(observations)

        return observations

    def get_historical_weather(
        self,
        location: GeoLocation,
        history_days: int = 90,
        refresh_if_missing: bool = True,
    ) -> list[HourlyClimateObservation]:
        """
        Return historical observations from repository.
        Fetch if missing.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=history_days)

        cached = self._weather_repository.get_observations(
            region=location.region,
            start_date=start_date,
            end_date=end_date,
        )

        if cached:
            return cached

        if not refresh_if_missing:
            return []

        return self.sync_historical_weather(
            location=location,
            history_days=history_days,
        )

    def get_forecast_weather(
        self,
        location: GeoLocation,
        forecast_days: int = 14,
        refresh_if_missing: bool = True,
    ) -> list[HourlyClimateObservation]:
        """
        Return forecast observations from repository.
        Fetch if missing.
        """
        cached = self._weather_repository.get_forecast(
            region=location.region,
            forecast_days=forecast_days,
        )

        if cached:
            return cached

        if not refresh_if_missing:
            return []

        return self.sync_forecast_weather(
            location=location,
            forecast_days=forecast_days,
        )

    def get_weather_context(
        self,
        location: GeoLocation,
        history_days: int = 90,
        forecast_days: int = 14,
    ) -> dict[str, list[HourlyClimateObservation]]:
        """
        Full biological weather context for simulation.
        """
        historical = self.get_historical_weather(
            location=location,
            history_days=history_days,
        )

        forecast = self.get_forecast_weather(
            location=location,
            forecast_days=forecast_days,
        )

        return {
            "historical": historical,
            "forecast": forecast,
        }

    def refresh_weather_context(
        self,
        location: GeoLocation,
        history_days: int = 90,
        forecast_days: int = 14,
    ) -> dict[str, list[HourlyClimateObservation]]:
        """
        Force refresh weather context.
        """
        historical = self.sync_historical_weather(
            location=location,
            history_days=history_days,
        )

        forecast = self.sync_forecast_weather(
            location=location,
            forecast_days=forecast_days,
        )

        return {
            "historical": historical,
            "forecast": forecast,
        }