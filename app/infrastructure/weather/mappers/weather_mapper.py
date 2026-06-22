from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.infrastructure.weather.dto.open_meteo_dto import OpenMeteoResponseDTO
from app.shared.kernel import HourlyClimateObservation
from app.shared.value_objects import GeoLocation


class WeatherMapper:
    """
    Maps external weather provider DTOs into canonical PestSense domain observations.
    """

    @staticmethod
    def open_meteo_to_hourly_observations(
        payload: OpenMeteoResponseDTO,
        region: str,
        source: str = "open_meteo",
        confidence: float = 0.92,
    ) -> list[HourlyClimateObservation]:
        if payload.hourly is None:
            return []

        hourly = payload.hourly

        provider_timezone = ZoneInfo(payload.timezone)

        location = GeoLocation(
            region=region,
            latitude=payload.latitude,
            longitude=payload.longitude,
            elevation_m=payload.elevation,
        )

        observations: list[HourlyClimateObservation] = []

        for index, timestamp_str in enumerate(hourly.time):
            local_timestamp = datetime.fromisoformat(timestamp_str).replace(
                tzinfo=provider_timezone
            )

            utc_timestamp = local_timestamp.astimezone(ZoneInfo("UTC"))

            missing_fields: list[str] = []

            wind_speed = None
            if hourly.wind_speed_10m is not None:
                wind_speed = hourly.wind_speed_10m[index]
            else:
                missing_fields.append("wind_speed_10m")

            pressure = None
            if hourly.pressure_msl is not None:
                pressure = hourly.pressure_msl[index]
            else:
                missing_fields.append("pressure_msl")

            cloud_cover = None
            if hourly.cloud_cover is not None:
                cloud_cover = hourly.cloud_cover[index]
            else:
                missing_fields.append("cloud_cover")

            observations.append(
                HourlyClimateObservation(
                    id=f"hourly_weather_{region}_{utc_timestamp.isoformat()}",
                    timestamp=utc_timestamp,
                    source=source,
                    confidence=confidence,
                    location=location,
                    temperature_c=hourly.temperature_2m[index],
                    humidity=hourly.relative_humidity_2m[index],
                    rainfall_mm=hourly.precipitation[index],
                    wind_speed_kph=wind_speed,
                    pressure_msl=pressure,
                    cloud_cover_pct=cloud_cover,
                    missing_fields=missing_fields,
                    metadata={
                        "provider": "open_meteo",
                        "provider_timezone": payload.timezone,
                        "provider_utc_offset_seconds": payload.utc_offset_seconds,
                        "original_local_timestamp": timestamp_str,
                    },
                )
            )

        return observations