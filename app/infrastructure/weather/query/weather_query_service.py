from __future__ import annotations

from datetime import date, timedelta

from app.domain.climate.contracts.weather_context import WeatherContext
from app.infrastructure.weather.services.weather_service import WeatherService
from app.shared.value_objects import GeoLocation


class WeatherQueryService:
    def __init__(
        self,
        weather_service: WeatherService,
    ):
        self.weather_service = weather_service

    def get_weather_context(
        self,
        location: GeoLocation,
        history_days: int = 30,
        forecast_days: int = 14,
    ) -> WeatherContext:
        historical = self.weather_service.get_historical_weather(
            location=location,
            history_days=history_days,
            refresh_if_missing=True,
        )

        forecast = self.weather_service.get_forecast_weather(
            location=location,
            forecast_days=forecast_days,
            refresh_if_missing=True,
        )

        current = historical[-1] if historical else None

        if current is None and forecast:
            current = forecast[0]

        if current is None:
            raise ValueError("No weather data available")

        return WeatherContext(
            location=location,
            historical=historical,
            current=current,
            forecast=forecast,
            confidence=0.95,
        )