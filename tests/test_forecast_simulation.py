from datetime import datetime, timedelta, timezone
from unittest import TestCase

from app.application import CurrentAnalysisWorkflow
from app.application.workflows.forecast_engine import ForecastSimulationEngine
from app.domain.climate import ClimateEngine
from app.domain.climate.contracts.weather_context import WeatherContext
from app.profiles import ProfileResolver, load_default_profiles
from app.shared.value_objects import GeoLocation


class ForecastSimulationTest(TestCase):
    def setUp(self) -> None:
        self.registry = load_default_profiles()
        self.resolver = ProfileResolver(self.registry)

        self.context = self.resolver.resolve_analysis_context(
            crop="crop_cotton",
            region="region_khanpur_tehsil",
            pests=[
                "pest_whitefly",
                "pest_jassid",
                "pest_mealybug",
            ],
        )

        self.location = GeoLocation(
            region="Khanpur Tehsil",
            latitude=28.6470,
            longitude=70.6560,
        )

        self.current_weather = WeatherContext(
            location=self.location,
            source="unit_test_current",
            confidence=0.92,
            current=self._weather_observation(
                timestamp=datetime(
                    2026,
                    6,
                    1,
                    12,
                    tzinfo=timezone.utc,
                ),
                temperature=34.0,
                humidity=62.0,
                rainfall=2.0,
            ),
        )

    def _weather_observation(
        self,
        timestamp,
        temperature,
        humidity,
        rainfall,
    ):
        from app.shared.kernel import HourlyClimateObservation

        return HourlyClimateObservation(
            id=f"weather_{timestamp.isoformat()}",
            timestamp=timestamp,
            source="unit_test",
            confidence=0.90,
            location=self.location,
            temperature_c=temperature,
            humidity=humidity,
            rainfall_mm=rainfall,
            wind_speed_kph=14.0,
        )

    def test_forecast_simulation_generates_projected_days(self) -> None:
        current_workflow = CurrentAnalysisWorkflow(self.registry)

        current_result = current_workflow.run(
            weather_context=self.current_weather,
            crop_profile=self.context.crop,
            pest_profiles=self.context.pests,
        )

        forecast_weather = WeatherContext(
            location=self.location,
            source="unit_test_forecast",
            confidence=0.88,
            forecast=[
                self._weather_observation(
                    timestamp=datetime(
                        2026,
                        6,
                        2 + day,
                        12,
                        tzinfo=timezone.utc,
                    ),
                    temperature=35.0 + day,
                    humidity=60.0,
                    rainfall=1.0,
                )
                for day in range(5)
            ],
        )

        climate_engine = ClimateEngine()

        projected_states = [
            climate_engine.compute_current_state(
                weather_context=WeatherContext(
                    location=self.location,
                    source="forecast_day",
                    confidence=forecast_weather.confidence,
                    current=observation,
                ),
                base_temperature=self.context.crop.thermal_base_temperature,
            )
            for observation in forecast_weather.forecast
        ]

        from app.shared.kernel import ClimateForecastTimeline

        climate_forecast = ClimateForecastTimeline(
            source="unit_test_forecast",
            projected_states=projected_states,
        )

        engine = ForecastSimulationEngine(self.registry)

        result = engine.run(
            current_crop_state=current_result.crop_state,
            current_pest_states=current_result.pest_states,
            climate_forecast=climate_forecast,
            crop_profile=self.context.crop,
            pest_profiles=self.context.pests,
        )

        self.assertEqual(len(result.projected_days), 5)
        self.assertEqual(len(result.confidence_curve), 5)
        self.assertTrue(len(result.summary) > 0)

    def test_forecast_confidence_decays(self) -> None:
        engine = ForecastSimulationEngine(self.registry)

        day1 = engine.apply_confidence_decay(0.90, 1)
        day3 = engine.apply_confidence_decay(0.90, 3)
        day7 = engine.apply_confidence_decay(0.90, 7)

        self.assertGreater(day1, day3)
        self.assertGreater(day3, day7)
        self.assertGreaterEqual(day7, 0.35)

    def test_outbreak_window_detection_returns_list(self) -> None:
        current_workflow = CurrentAnalysisWorkflow(self.registry)

        current_result = current_workflow.run(
            weather_context=self.current_weather,
            crop_profile=self.context.crop,
            pest_profiles=self.context.pests,
        )

        forecast_weather = [
            self._weather_observation(
                timestamp=datetime(
                    2026,
                    6,
                    10 + i,
                    12,
                    tzinfo=timezone.utc,
                ),
                temperature=38.0,
                humidity=70.0,
                rainfall=0.0,
            )
            for i in range(3)
        ]

        climate_engine = ClimateEngine()

        projected_states = [
            climate_engine.compute_current_state(
                weather_context=WeatherContext(
                    location=self.location,
                    current=obs,
                    source="forecast_test",
                    confidence=0.85,
                ),
                base_temperature=self.context.crop.thermal_base_temperature,
            )
            for obs in forecast_weather
        ]

        from app.shared.kernel import ClimateForecastTimeline

        climate_forecast = ClimateForecastTimeline(
            source="forecast_test",
            projected_states=projected_states,
        )

        engine = ForecastSimulationEngine(self.registry)

        result = engine.run(
            current_crop_state=current_result.crop_state,
            current_pest_states=current_result.pest_states,
            climate_forecast=climate_forecast,
            crop_profile=self.context.crop,
            pest_profiles=self.context.pests,
        )

        self.assertIsInstance(result.outbreak_windows, list)
        self.assertIsInstance(result.intervention_windows, list)