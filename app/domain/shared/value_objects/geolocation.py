from __future__ import annotations

from pydantic import Field

from app.domain.shared.base.value_object import ValueObject


class GeoLocation(ValueObject):
    """
    Geographic location descriptor for environmental
    and agricultural domain context.

    Supports coarse regional context and optional
    precise coordinates.
    """

    region: str = Field(
        min_length=1,
        description="Human-readable regional identifier.",
    )

    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="Latitude in decimal degrees.",
    )

    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="Longitude in decimal degrees.",
    )

    elevation_m: float | None = Field(
        default=None,
        description="Elevation above mean sea level in meters.",
    )