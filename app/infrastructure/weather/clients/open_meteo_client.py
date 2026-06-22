# app/infrastructure/weather/clients/open_meteo_client.py
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

import httpx

from app.core.settings import settings
from app.infrastructure.weather.dto.open_meteo_dto import OpenMeteoResponseDTO
from app.infrastructure.weather.exceptions import (
    WeatherProviderRequestError,
    WeatherProviderResponseError,
)


class OpenMeteoClient:
    """
    Open-Meteo weather provider adapter.

    Responsibilities:
    - external API communication
    - request parameter construction
    - response validation via DTOs

    NOT responsible for:
    - domain mapping
    - biological calculations
    - persistence
    """

    FORECAST_BASE_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    HOURLY_FIELDS = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "pressure_msl",
        "cloud_cover",
    ]

    def __init__(
        self,
        timeout_seconds: Optional[float] = None,
        user_agent: str = "PestSense/1.0",
    ) -> None:
        self._timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.HTTP_TIMEOUT_SECONDS
        )

        self._headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }

    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 14,
    ) -> OpenMeteoResponseDTO:
        """
        Fetch hourly forecast weather.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(self.HOURLY_FIELDS),
            "forecast_days": forecast_days,
            "timezone": "auto",
        }

        payload = self._request(
            url=self.FORECAST_BASE_URL,
            params=params,
        )

        return self._parse_response(payload)

    def get_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> OpenMeteoResponseDTO:
        """
        Fetch hourly historical weather.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": ",".join(self.HOURLY_FIELDS),
            "timezone": "auto",
        }

        payload = self._request(
            url=self.ARCHIVE_BASE_URL,
            params=params,
        )

        return self._parse_response(payload)

    def get_current_plus_history(
        self,
        latitude: float,
        longitude: float,
        history_days: int,
        end_date: Optional[date] = None,
    ) -> OpenMeteoResponseDTO:
        """
        Convenience method for biological state reconstruction.
        """
        effective_end = end_date or date.today()
        start = effective_end - timedelta(days=history_days)

        return self.get_historical(
            latitude=latitude,
            longitude=longitude,
            start_date=start,
            end_date=effective_end,
        )

    def _request(
        self,
        url: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            with httpx.Client(
                timeout=self._timeout_seconds,
                headers=self._headers,
            ) as client:
                response = client.get(
                    url,
                    params=params,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as exc:
            raise WeatherProviderRequestError(
                f"Open-Meteo HTTP error: {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise WeatherProviderRequestError(
                f"Open-Meteo request failed: {exc}"
            ) from exc

        except ValueError as exc:
            raise WeatherProviderResponseError(
                "Open-Meteo returned invalid JSON"
            ) from exc

    def _parse_response(
        self,
        payload: dict[str, Any],
    ) -> OpenMeteoResponseDTO:
        try:
            return OpenMeteoResponseDTO.model_validate(payload)

        except Exception as exc:
            raise WeatherProviderResponseError(
                f"Open-Meteo payload validation failed: {exc}"
            ) from exc