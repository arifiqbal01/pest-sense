# app/infrastructure/weather/repositories/weather_repository.py
from __future__ import annotations

from datetime import date
from typing import Protocol

from app.shared.kernel import HourlyClimateObservation


class WeatherRepository(Protocol):
    """
    Weather persistence contract.

    Infrastructure implementations may use:
    - PostgreSQL
    - TimescaleDB
    - SQLite (MVP only)
    - Redis cache
    - file storage

    Domain/services depend only on this contract.
    """

    def save_observations(
        self,
        observations: list[HourlyClimateObservation],
    ) -> None:
        """
        Persist historical observed weather.
        """
        ...

    def save_forecast(
        self,
        observations: list[HourlyClimateObservation],
    ) -> None:
        """
        Persist forecast weather snapshots.
        """
        ...

    def get_observations(
        self,
        region: str,
        start_date: date,
        end_date: date,
    ) -> list[HourlyClimateObservation]:
        """
        Retrieve historical weather observations.
        """
        ...

    def get_forecast(
        self,
        region: str,
        forecast_days: int,
    ) -> list[HourlyClimateObservation]:
        """
        Retrieve forecast weather observations.
        """
        ...

    def delete_forecast(
        self,
        region: str,
    ) -> None:
        """
        Remove stale forecast records before replacement.
        """
        ...

    def observation_exists(
        self,
        region: str,
        start_date: date,
        end_date: date,
    ) -> bool:
        """
        Fast existence check for cache decisions.
        """
        ...

    def forecast_exists(
        self,
        region: str,
    ) -> bool:
        """
        Fast forecast cache existence check.
        """
        ...