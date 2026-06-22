from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WeatherDTO(BaseModel):
    """
    Base DTO for external weather provider contracts.

    External providers may add extra fields over time.
    We ignore unknown payload keys to avoid brittle integrations.
    """

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
    )


# =========================
# OPEN-METEO UNITS DTO
# =========================

class OpenMeteoHourlyUnitsDTO(WeatherDTO):
    time: str
    temperature_2m: str
    relative_humidity_2m: str
    precipitation: str

    wind_speed_10m: Optional[str] = None
    pressure_msl: Optional[str] = None
    cloud_cover: Optional[str] = None


# =========================
# OPEN-METEO HOURLY DTO
# =========================

class OpenMeteoHourlyDTO(WeatherDTO):
    time: list[str]

    temperature_2m: list[float]

    relative_humidity_2m: list[float]

    precipitation: list[float]

    wind_speed_10m: Optional[list[float]] = None

    pressure_msl: Optional[list[float]] = None

    cloud_cover: Optional[list[float]] = None

    @model_validator(mode="after")
    def validate_parallel_lengths(self) -> "OpenMeteoHourlyDTO":
        expected = len(self.time)

        required_fields = [
            self.temperature_2m,
            self.relative_humidity_2m,
            self.precipitation,
        ]

        optional_fields = [
            self.wind_speed_10m,
            self.pressure_msl,
            self.cloud_cover,
        ]

        for field in required_fields:
            if len(field) != expected:
                raise ValueError(
                    "hourly weather arrays must match time array length"
                )

        for field in optional_fields:
            if field is not None and len(field) != expected:
                raise ValueError(
                    "optional hourly weather arrays must match time array length"
                )

        return self


# =========================
# OPEN-METEO DAILY DTO
# =========================

class OpenMeteoDailyDTO(WeatherDTO):
    time: list[str]

    temperature_2m_max: list[float]

    temperature_2m_min: list[float]

    precipitation_sum: list[float]

    wind_speed_10m_max: Optional[list[float]] = None

    @model_validator(mode="after")
    def validate_parallel_lengths(self) -> "OpenMeteoDailyDTO":
        expected = len(self.time)

        required_fields = [
            self.temperature_2m_max,
            self.temperature_2m_min,
            self.precipitation_sum,
        ]

        optional_fields = [
            self.wind_speed_10m_max,
        ]

        for field in required_fields:
            if len(field) != expected:
                raise ValueError(
                    "daily weather arrays must match time array length"
                )

        for field in optional_fields:
            if field is not None and len(field) != expected:
                raise ValueError(
                    "optional daily weather arrays must match time array length"
                )

        return self


# =========================
# ROOT RESPONSE DTO
# =========================

class OpenMeteoResponseDTO(WeatherDTO):
    latitude: float
    longitude: float
    generationtime_ms: Optional[float] = None
    utc_offset_seconds: int = 0
    timezone: str
    timezone_abbreviation: Optional[str] = None
    elevation: Optional[float] = None

    hourly_units: Optional[OpenMeteoHourlyUnitsDTO] = None

    hourly: Optional[OpenMeteoHourlyDTO] = None

    daily: Optional[OpenMeteoDailyDTO] = None

    @model_validator(mode="after")
    def validate_payload(self) -> "OpenMeteoResponseDTO":
        if self.hourly is None and self.daily is None:
            raise ValueError(
                "open-meteo response must contain hourly or daily data"
            )

        return self


# =========================
# CANONICAL INTERNAL DTO
# =========================

class WeatherObservationDTO(WeatherDTO):
    """
    Provider-neutral normalized transport DTO.
    """

    timestamp: str

    temperature_c: float

    humidity_pct: float = Field(
        ge=0.0,
        le=100.0,
    )

    rainfall_mm: float = Field(
        ge=0.0,
    )

    wind_speed_kph: Optional[float] = Field(
        default=None,
        ge=0.0,
    )

    pressure_msl: Optional[float] = None

    cloud_cover_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )