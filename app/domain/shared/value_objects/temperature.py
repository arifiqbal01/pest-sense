from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from app.domain.shared.base.value_object import ValueObject


class Temperature(ValueObject):
    """
    Atomic temperature measurement.

    Represents a single temperature reading.
    Suitable for hourly observations and general scientific use.
    """

    value: float

    unit: str = Field(
        default="celsius",
        description="Temperature unit.",
    )

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, value: str) -> str:
        normalized = value.lower()

        if normalized not in {"celsius", "fahrenheit"}:
            raise ValueError(
                "Temperature unit must be 'celsius' or 'fahrenheit'."
            )

        return normalized

    def celsius(self) -> float:
        """
        Return normalized Celsius value.
        """
        if self.unit == "fahrenheit":
            return (self.value - 32.0) * 5.0 / 9.0

        return self.value

    def fahrenheit(self) -> float:
        """
        Return normalized Fahrenheit value.
        """
        if self.unit == "celsius":
            return (self.value * 9.0 / 5.0) + 32.0

        return self.value

    def difference(self, other: "Temperature") -> float:
        """
        Compare difference in Celsius.
        """
        return self.celsius() - other.celsius()


class TemperatureRange(ValueObject):
    """
    Scientific thermal range definition.

    Used for:
    - pest thermal profiles
    - crop thermal thresholds
    - environmental suitability logic
    """

    minimum: float
    maximum: float

    @model_validator(mode="after")
    def validate_range(self) -> "TemperatureRange":
        if self.maximum < self.minimum:
            raise ValueError(
                "Maximum temperature must be greater than or equal to minimum."
            )
        return self

    @property
    def midpoint(self) -> float:
        return (self.minimum + self.maximum) / 2.0

    def contains(self, temperature_c: float) -> bool:
        return self.minimum <= temperature_c <= self.maximum


class DailyTemperature(ValueObject):
    """
    Daily aggregated environmental temperature summary.

    Daily abstraction for forecast APIs and historical summaries.
    """

    minimum: float
    maximum: float
    average: float | None = None

    @model_validator(mode="after")
    def validate_values(self) -> "DailyTemperature":
        if self.maximum < self.minimum:
            raise ValueError(
                "Daily maximum temperature must be >= daily minimum."
            )

        if (
            self.average is not None
            and not self.minimum <= self.average <= self.maximum
        ):
            raise ValueError(
                "Daily average temperature must fall between minimum and maximum."
            )

        return self

    @property
    def mean(self) -> float:
        """
        Derived daily mean.
        """
        return (
            self.average
            if self.average is not None
            else (self.minimum + self.maximum) / 2.0
        )

    @property
    def diurnal_range(self) -> float:
        """
        Daily thermal swing.
        """
        return self.maximum - self.minimum