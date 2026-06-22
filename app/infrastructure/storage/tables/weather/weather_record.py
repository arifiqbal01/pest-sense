from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.storage.db.base import Base, TimestampMixin


class WeatherRecord(Base, TimestampMixin):
    __tablename__ = "weather_records"

    __table_args__ = (
        UniqueConstraint(
            "region",
            "timestamp",
            "is_forecast",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    region: Mapped[str] = mapped_column(String(120))

    latitude: Mapped[Optional[float]] = mapped_column(Float)

    longitude: Mapped[Optional[float]] = mapped_column(Float)

    elevation_m: Mapped[Optional[float]] = mapped_column(Float)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    temperature_c: Mapped[float] = mapped_column(Float)

    humidity: Mapped[float] = mapped_column(Float)

    rainfall_mm: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    wind_speed_kph: Mapped[Optional[float]] = mapped_column(Float)

    pressure_msl: Mapped[Optional[float]] = mapped_column(Float)

    cloud_cover_pct: Mapped[Optional[float]] = mapped_column(Float)

    source: Mapped[str] = mapped_column(String(50))

    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
    )

    is_forecast: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    forecast_generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
    )