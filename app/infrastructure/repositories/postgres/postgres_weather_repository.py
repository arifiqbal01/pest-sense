# app/infrastructure/repositories/postgres/postgres_weather_repository.py
from __future__ import annotations

from datetime import date, datetime, time, timezone

from sqlalchemy import delete, select

from app.infrastructure.weather.repositories.weather_repository import (
    WeatherRepository,
)
from app.shared.kernel import HourlyClimateObservation
from app.shared.value_objects import GeoLocation

from app.infrastructure.storage.db.session import SessionLocal
from app.infrastructure.storage.tables.weather.weather_record import WeatherRecord


class PostgreSQLWeatherRepository(WeatherRepository):
    """
    PostgreSQL weather persistence adapter.
    """

    def save_observations(
        self,
        observations: list[HourlyClimateObservation],
    ) -> None:
        if not observations:
            return

        with SessionLocal() as session:
            for obs in observations:
                existing = session.execute(
                    select(WeatherRecord).where(
                        WeatherRecord.region == obs.location.region,
                        WeatherRecord.timestamp == obs.timestamp,
                        WeatherRecord.is_forecast.is_(False),
                    )
                ).scalar_one_or_none()

                if existing:
                    continue

                session.add(self._to_record(obs, is_forecast=False))

            session.commit()

    def save_forecast(
        self,
        observations: list[HourlyClimateObservation],
    ) -> None:
        if not observations:
            return

        region = observations[0].location.region

        with SessionLocal() as session:
            session.execute(
                delete(WeatherRecord).where(
                    WeatherRecord.region == region,
                    WeatherRecord.is_forecast.is_(True),
                )
            )

            for obs in observations:
                session.add(self._to_record(obs, is_forecast=True))

            session.commit()

    def get_observations(
        self,
        region: str,
        start_date: date,
        end_date: date,
    ) -> list[HourlyClimateObservation]:
        start_dt = datetime.combine(
            start_date,
            time.min,
            tzinfo=timezone.utc,
        )

        end_dt = datetime.combine(
            end_date,
            time.max,
            tzinfo=timezone.utc,
        )

        with SessionLocal() as session:
            rows = session.execute(
                select(WeatherRecord)
                .where(
                    WeatherRecord.region == region,
                    WeatherRecord.is_forecast.is_(False),
                    WeatherRecord.timestamp >= start_dt,
                    WeatherRecord.timestamp <= end_dt,
                )
                .order_by(WeatherRecord.timestamp.asc())
            ).scalars().all()

        return [self._to_domain(row) for row in rows]

    def get_forecast(
        self,
        region: str,
        forecast_days: int,
    ) -> list[HourlyClimateObservation]:
        now = datetime.now(timezone.utc)

        with SessionLocal() as session:
            rows = session.execute(
                select(WeatherRecord)
                .where(
                    WeatherRecord.region == region,
                    WeatherRecord.is_forecast.is_(True),
                    WeatherRecord.timestamp >= now,
                )
                .order_by(WeatherRecord.timestamp.asc())
            ).scalars().all()

        return [self._to_domain(row) for row in rows]

    def delete_forecast(
        self,
        region: str,
    ) -> None:
        with SessionLocal() as session:
            session.execute(
                delete(WeatherRecord).where(
                    WeatherRecord.region == region,
                    WeatherRecord.is_forecast.is_(True),
                )
            )
            session.commit()

    def observation_exists(
        self,
        region: str,
        start_date: date,
        end_date: date,
    ) -> bool:
        return bool(
            self.get_observations(
                region=region,
                start_date=start_date,
                end_date=end_date,
            )
        )

    def forecast_exists(
        self,
        region: str,
    ) -> bool:
        return bool(
            self.get_forecast(
                region=region,
                forecast_days=14,
            )
        )

    @staticmethod
    def _to_record(
        observation: HourlyClimateObservation,
        is_forecast: bool,
    ) -> WeatherRecord:
        return WeatherRecord(
            region=observation.location.region,
            latitude=observation.location.latitude,
            longitude=observation.location.longitude,
            elevation_m=observation.location.elevation_m,
            timestamp=observation.timestamp,
            temperature_c=observation.temperature_c,
            humidity=observation.humidity,
            rainfall_mm=observation.rainfall_mm,
            wind_speed_kph=observation.wind_speed_kph,
            pressure_msl=observation.pressure_msl,
            cloud_cover_pct=observation.cloud_cover_pct,
            source=observation.source,
            confidence=observation.confidence,
            is_forecast=is_forecast,
        )

    @staticmethod
    def _to_domain(
        row: WeatherRecord,
    ) -> HourlyClimateObservation:
        return HourlyClimateObservation(
            id=f"weather_{row.region}_{row.timestamp.isoformat()}",
            timestamp=row.timestamp,
            source=row.source,
            confidence=row.confidence,
            location=GeoLocation(
                region=row.region,
                latitude=row.latitude,
                longitude=row.longitude,
                elevation_m=row.elevation_m,
            ),
            temperature_c=row.temperature_c,
            humidity=row.humidity,
            rainfall_mm=row.rainfall_mm,
            wind_speed_kph=row.wind_speed_kph,
            pressure_msl=row.pressure_msl,
            cloud_cover_pct=row.cloud_cover_pct,
            metadata={
                "is_forecast": row.is_forecast,
            },
        )