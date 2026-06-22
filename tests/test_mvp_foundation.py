from datetime import datetime, timezone
from unittest import TestCase

from app.application import CurrentAnalysisWorkflow, ValidationWorkflow
from app.domain.climate.contracts.weather_context import WeatherContext
from app.domain.validation import FieldObservation, ValidationEngine
from app.profiles import ProfileResolver, load_default_profiles
from app.shared.kernel import HourlyClimateObservation
from app.shared.value_objects import GeoLocation


class MvpFoundationTest(TestCase):
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

        self.current_observation = HourlyClimateObservation(
            id="weather_test_001",
            timestamp=datetime(
                2026,
                6,
                1,
                12,
                tzinfo=timezone.utc,
            ),
            source="unit_test",
            confidence=0.91,
            location=GeoLocation(
                region="Khanpur Tehsil",
                latitude=28.6470,
                longitude=70.6560,
            ),
            temperature_c=34.0,
            humidity=62.0,
            rainfall_mm=2.0,
            wind_speed_kph=14.0,
        )

        self.weather_context = WeatherContext(
            location=self.current_observation.location,
            historical=[],
            current=self.current_observation,
            forecast=[],
            source="unit_test_weather",
            confidence=0.91,
        )

    def test_profiles_load_successfully(self) -> None:
        self.assertEqual(self.context.crop.crop_type, "cotton")
        self.assertEqual(self.context.region.id, "region_khanpur_tehsil")
        self.assertEqual(len(self.context.pests), 3)
        self.assertGreaterEqual(len(self.context.treatments), 1)

    def test_profile_registry_lookup(self) -> None:
        crop = self.registry.get_crop_profile("crop_cotton")
        pest = self.registry.get_pest_profile("pest_whitefly")
        region = self.registry.get_region_profile("region_khanpur_tehsil")

        self.assertEqual(crop.id, "crop_cotton")
        self.assertEqual(pest.id, "pest_whitefly")
        self.assertEqual(region.id, "region_khanpur_tehsil")

    def test_current_analysis_workflow_generates_states(self) -> None:
        workflow = CurrentAnalysisWorkflow(self.registry)

        result = workflow.run(
            weather_context=self.weather_context,
            crop_profile=self.context.crop,
            pest_profiles=self.context.pests,
        )

        self.assertEqual(result.climate_state.type, "ClimateState")
        self.assertEqual(result.crop_state.type, "CropState")

        self.assertEqual(len(result.pest_states), 3)
        self.assertEqual(len(result.suitability_states), 3)
        self.assertEqual(len(result.risk_states), 3)
        self.assertEqual(len(result.recommendations), 3)

    def test_biological_outputs_are_valid(self) -> None:
        workflow = CurrentAnalysisWorkflow(self.registry)

        result = workflow.run(
            weather_context=self.weather_context,
            crop_profile=self.context.crop,
            pest_profiles=self.context.pests,
        )

        for suitability in result.suitability_states:
            self.assertGreaterEqual(
                suitability.overall_suitability,
                0.0,
            )

        for risk in result.risk_states:
            self.assertGreaterEqual(
                risk.risk_score,
                0.0,
            )

        for recommendation in result.recommendations:
            self.assertIsNotNone(
                recommendation.target_pest
            )

    def test_validation_workflow_compares_prediction(self) -> None:
        workflow = CurrentAnalysisWorkflow(self.registry)

        current = workflow.run(
            weather_context=self.weather_context,
            crop_profile=self.context.crop,
            pest_profiles=[self.context.pests[0]],
        )

        validator = ValidationEngine()

        prediction = validator.build_prediction_snapshot(
            risk_state=current.risk_states[0],
            pest_state=current.pest_states[0],
            region=self.context.region.name,
            crop_id=self.context.crop.id,
            recommendation=current.recommendations[0],
        )

        observation = FieldObservation(
            observation_id="obs_001",
            timestamp=datetime(
                2026,
                6,
                1,
                16,
                tzinfo=timezone.utc,
            ),
            location=GeoLocation(
                region=self.context.region.name
            ),
            crop_stage=current.crop_state.current_stage,
            observed_pest_stage=current.pest_states[0].current_stage,
            observed_population_pressure=current.pest_states[0].population_pressure.level,
            observed_damage_level="low",
            actual_outbreak=False,
            observer_confidence=0.82,
        )

        result = ValidationWorkflow().run(
            prediction=prediction,
            observation=observation,
        )

        self.assertEqual(
            result.prediction_id,
            current.risk_states[0].id,
        )

        self.assertGreaterEqual(
            result.prediction_accuracy,
            0.0,
        )

        self.assertFalse(result.false_negative)
        self.assertTrue(result.learning_insights)