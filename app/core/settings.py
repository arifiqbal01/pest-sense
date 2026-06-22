from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class WeatherProvider(str, Enum):
    OPEN_METEO = "open_meteo"
    TOMORROW_IO = "tomorrow_io"
    OPENWEATHER = "openweather"


class Settings(BaseSettings):
    """
    Central application configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
        env_file_encoding="utf-8",
    )

    APP_NAME: str = "PestSense"
    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT
    DEBUG: bool = False

    DATABASE_URL: str

    HTTP_TIMEOUT_SECONDS: float = Field(
        default=30.0,
        gt=0,
    )

    WEATHER_PROVIDER: WeatherProvider = WeatherProvider.OPEN_METEO
    WEATHER_FORECAST_DAYS: int = Field(
        default=14,
        ge=1,
        le=30,
    )

    WEATHER_HISTORY_DAYS: int = Field(
        default=90,
        ge=1,
        le=365,
    )

    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com"
    OPEN_METEO_ARCHIVE_URL: str = "https://archive-api.open-meteo.com"

    REDIS_URL: str | None = None

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == AppEnvironment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == AppEnvironment.DEVELOPMENT

    @property
    def is_test(self) -> bool:
        return self.APP_ENV == AppEnvironment.TEST


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = Settings()