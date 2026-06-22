from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Optional

from app.domain.climate.contracts.weather_context import WeatherContext
from app.domain.shared.enums import EnvironmentalEventType, SeverityLevel
from app.domain.shared.contracts import (
    ClimateForecastTimeline,
    ClimateState,
    EnvironmentalMetricState,
    HourlyClimateObservation,
)
from app.domain.shared.value_objects import Anomaly, DegreeDay


class HourlyGDDStrategy:
    method = "hourly_integration"

    def calculate(
        self,
        observations: list[HourlyClimateObservation],
        base_temperature: float,
        previous_accumulated_gdd: float = 0.0,
    ) -> DegreeDay:
        if not observations:
            return DegreeDay(
                daily_value=0.0,
                accumulated_value=previous_accumulated_gdd,
                calculation_method=self.method,
                confidence=0.0,
            )

        thermal_units = sum(
            max(0.0, obs.temperature_c - base_temperature) / 24.0
            for obs in observations
        )

        confidence = mean(obs.confidence for obs in observations)

        return DegreeDay(
            daily_value=thermal_units,
            accumulated_value=previous_accumulated_gdd + thermal_units,
            calculation_method=self.method,
            confidence=confidence,
        )


class ClimateEngine:
    """
    Environmental intelligence only.

    No pest logic.
    No crop logic.
    """

    HUMIDITY_THRESHOLD = 80.0
    HEAT_THRESHOLD = 38.0
    SEVERE_HEAT_THRESHOLD = 42.0
    COLD_THRESHOLD = 10.0
    HEAVY_RAIN_THRESHOLD = 25.0

    def __init__(
        self,
        gdd_strategy: Optional[HourlyGDDStrategy] = None,
    ):
        self.gdd_strategy = gdd_strategy or HourlyGDDStrategy()

    def compute_current_state(
        self,
        weather_context: WeatherContext,
        base_temperature: float,
        previous_accumulated_gdd: float = 0.0,
    ) -> ClimateState:
        if not weather_context.current:
            raise ValueError("WeatherContext missing current observation")

        observations = [
            self._normalize_observation(obs)
            for obs in (
                weather_context.historical
                + [weather_context.current]
            )
        ]

        self._validate_observations(observations)

        metrics = self._build_metrics(observations)

        degree_day = self.gdd_strategy.calculate(
            observations=self._last_n(observations, 24),
            base_temperature=base_temperature,
            previous_accumulated_gdd=previous_accumulated_gdd,
        )

        anomalies = self.detect_anomalies(observations)

        events = self.detect_environmental_events(metrics)

        if len(observations) >= 72 and metrics.rainfall_7d <= 2.0:
            events.append(EnvironmentalEventType.DROUGHT)

        confidence = min(
            weather_context.confidence,
            degree_day.confidence,
        )

        return ClimateState(
            id=f"climate_state_{weather_context.current.id}",
            timestamp=weather_context.current.timestamp,
            source=weather_context.source,
            confidence=confidence,
            location=weather_context.location,
            current_conditions=weather_context.current,
            degree_day=degree_day,
            metrics=metrics,
            accumulated_gdd=degree_day.accumulated_value,
            anomalies=anomalies,
            environmental_events=events,
            reasoning=self._build_reasoning(
                degree_day,
                anomalies,
                events,
            ),
        )

    def compute_forecast_timeline(
        self,
        weather_context: WeatherContext,
        base_temperature: float,
        current_accumulated_gdd: float,
    ) -> ClimateForecastTimeline:
        grouped = self._group_by_day(weather_context.forecast)

        projected_states = []

        running_gdd = current_accumulated_gdd

        for day_obs in grouped.values():
            synthetic_context = WeatherContext(
                location=weather_context.location,
                historical=[],
                current=day_obs[-1],
                forecast=[],
                source=weather_context.source,
                confidence=mean(obs.confidence for obs in day_obs),
            )

            state = self.compute_current_state(
                weather_context=synthetic_context,
                base_temperature=base_temperature,
                previous_accumulated_gdd=running_gdd,
            )

            running_gdd = state.accumulated_gdd

            projected_states.append(state)

        return ClimateForecastTimeline(
            source=weather_context.source,
            projected_states=projected_states,
        )

    def detect_anomalies(
        self,
        observations: list[HourlyClimateObservation],
    ) -> list[Anomaly]:
        anomalies = []

        latest = observations[-1]

        if any(
            obs.temperature_c >= self.SEVERE_HEAT_THRESHOLD
            for obs in observations
        ):
            anomalies.append(
                Anomaly(
                    anomaly_type=EnvironmentalEventType.HEATWAVE,
                    severity=SeverityLevel.SEVERE,
                    detected_at=latest.timestamp,
                    expected_impact="extreme thermal stress",
                    confidence=0.9,
                )
            )

        if any(
            obs.temperature_c <= self.COLD_THRESHOLD
            for obs in observations
        ):
            anomalies.append(
                Anomaly(
                    anomaly_type=EnvironmentalEventType.COLD_STRESS,
                    severity=SeverityLevel.MODERATE,
                    detected_at=latest.timestamp,
                    expected_impact="cold environmental stress",
                    confidence=0.8,
                )
            )

        if self._thermal_volatility(observations) >= 12.0:
            anomalies.append(
                Anomaly(
                    anomaly_type=EnvironmentalEventType.RAPID_TEMPERATURE_DROP,
                    severity=SeverityLevel.MODERATE,
                    detected_at=latest.timestamp,
                    expected_impact="rapid thermal volatility",
                    confidence=0.7,
                )
            )

        if (
            len(observations) >= 72
            and self._sum_rainfall(self._last_n(observations, 168)) <= 2.0
        ):
            anomalies.append(
                Anomaly(
                    anomaly_type=EnvironmentalEventType.DROUGHT,
                    severity=SeverityLevel.MODERATE,
                    detected_at=latest.timestamp,
                    expected_impact="dry environmental forcing",
                    confidence=0.75,
                )
            )

        return anomalies

    def detect_environmental_events(
        self,
        metrics: EnvironmentalMetricState,
    ) -> list[EnvironmentalEventType]:
        events = []

        if metrics.rainfall_24h >= self.HEAVY_RAIN_THRESHOLD:
            events.append(EnvironmentalEventType.HEAVY_RAINFALL)

        if metrics.humid_hours_72h >= 24:
            events.append(EnvironmentalEventType.PROLONGED_HUMIDITY)

        if metrics.heat_stress_hours_72h >= 12:
            events.append(EnvironmentalEventType.HEATWAVE)

        if metrics.cold_stress_hours_72h >= 12:
            events.append(EnvironmentalEventType.COLD_STRESS)

        return events

    def _build_metrics(
        self,
        observations: list[HourlyClimateObservation],
    ) -> EnvironmentalMetricState:
        return EnvironmentalMetricState(
            temperature_mean_24h=self._mean_temp(
                self._last_n(observations, 24)
            ),
            temperature_mean_72h=self._mean_temp(
                self._last_n(observations, 72)
            ),
            humidity_mean_24h=self._mean_humidity(
                self._last_n(observations, 24)
            ),
            humidity_mean_72h=self._mean_humidity(
                self._last_n(observations, 72)
            ),
            rainfall_24h=self._sum_rainfall(
                self._last_n(observations, 24)
            ),
            rainfall_72h=self._sum_rainfall(
                self._last_n(observations, 72)
            ),
            rainfall_7d=self._sum_rainfall(
                self._last_n(observations, 168)
            ),
            humid_hours_72h=self._humid_hours(
                self._last_n(observations, 72)
            ),
            heat_stress_hours_72h=self._heat_hours(
                self._last_n(observations, 72)
            ),
            cold_stress_hours_72h=self._cold_hours(
                self._last_n(observations, 72)
            ),
        )

    def _last_n(self, observations, n):
        return observations[-n:] if observations else []

    def _mean_temp(self, observations):
        if not observations:
            return 0.0
        return mean(obs.temperature_c for obs in observations)

    def _mean_humidity(self, observations):
        if not observations:
            return 0.0
        return mean(obs.humidity for obs in observations)

    def _sum_rainfall(self, observations):
        return sum(obs.rainfall_mm for obs in observations)

    def _humid_hours(self, observations):
        return sum(
            1
            for obs in observations
            if obs.humidity >= self.HUMIDITY_THRESHOLD
        )

    def _heat_hours(self, observations):
        return sum(
            1
            for obs in observations
            if obs.temperature_c >= self.HEAT_THRESHOLD
        )

    def _cold_hours(self, observations):
        return sum(
            1
            for obs in observations
            if obs.temperature_c <= self.COLD_THRESHOLD
        )

    def _group_by_day(self, observations):
        grouped = defaultdict(list)

        for obs in observations:
            grouped[obs.timestamp.date()].append(obs)

        return grouped

    def _normalize_observation(
        self,
        observation: HourlyClimateObservation,
    ) -> HourlyClimateObservation:
        missing_fields = list(observation.missing_fields)

        if observation.pressure_msl is None:
            missing_fields.append("pressure_msl")

        if observation.cloud_cover_pct is None:
            missing_fields.append("cloud_cover_pct")

        return observation.model_copy(
            update={
                "temperature_c": float(observation.temperature_c),
                "humidity": max(0.0, min(100.0, float(observation.humidity))),
                "rainfall_mm": max(0.0, float(observation.rainfall_mm)),
                "missing_fields": sorted(set(missing_fields)),
            }
        )

    def _validate_observations(
        self,
        observations: list[HourlyClimateObservation],
    ) -> None:
        previous_timestamp = None

        for observation in observations:
            if not -60.0 <= observation.temperature_c <= 65.0:
                raise ValueError("temperature outside physical plausibility range")

            if previous_timestamp and observation.timestamp < previous_timestamp:
                raise ValueError("weather observations must be timestamp ordered")

            previous_timestamp = observation.timestamp

    def _thermal_volatility(
        self,
        observations: list[HourlyClimateObservation],
    ) -> float:
        recent = self._last_n(observations, 24)

        if len(recent) < 2:
            return 0.0

        temperatures = [obs.temperature_c for obs in recent]
        return max(temperatures) - min(temperatures)

    def _build_reasoning(
        self,
        degree_day,
        anomalies,
        events,
    ):
        reasoning = [
            f"Hourly thermal accumulation: {degree_day.daily_value:.2f}"
        ]

        if anomalies:
            reasoning.append(
                f"Detected {len(anomalies)} environmental anomalies"
            )

        if events:
            reasoning.append(
                "Environmental events: " +
                ", ".join(event.value for event in events)
            )

        return reasoning
