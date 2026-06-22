from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.orchestrators import CurrentAnalysisWorkflow
from app.orchestrators.forecast_simulation import ForecastSimulationEngine
from app.profiles import load_default_profiles
from app.scripts.run_current_simulation import sample_climate_snapshot
from app.shared.kernel import ForecastClimateTimeline, ForecastDay
from app.shared.value_objects import DailyTemperature, TimeWindow


def main() -> None:
    profiles = load_default_profiles()
    crop_profile = profiles.get_crop_profile("crop_cotton")
    pest_profile = profiles.get_pest_profile("pest_whitefly")
    current = CurrentAnalysisWorkflow(profiles).run(
        climate_snapshot=sample_climate_snapshot(),
        crop_profile=crop_profile,
        pest_profiles=[pest_profile],
        sowing_date=date(2026, 5, 1),
    )
    timeline = ForecastSimulationEngine(profiles).run(
        current_climate_state=current.climate_state,
        current_crop_state=current.crop_state,
        current_pest_states=current.pest_states,
        forecast_timeline=sample_forecast_timeline(),
        crop_profile=crop_profile,
        pest_profiles=[pest_profile],
    )
    print_forecast_timeline(timeline)


def sample_forecast_timeline() -> ForecastClimateTimeline:
    start = date(2026, 6, 2)
    averages = [35.0, 35.5, 34.5, 33.5, 32.5, 34.0, 35.0]
    humidities = [66, 68, 70, 72, 74, 69, 65]
    rainfall = [1, 0, 3, 6, 2, 0, 0]
    confidences = [0.86, 0.82, 0.78, 0.73, 0.68, 0.63, 0.58]
    days = []
    for index, average in enumerate(averages):
        days.append(
            ForecastDay(
                simulation_date=start + timedelta(days=index),
                predicted_temperature=DailyTemperature(
                    minimum=average - 5.5,
                    maximum=average + 5.0,
                    average=average,
                ),
                predicted_humidity=humidities[index],
                predicted_rainfall_mm=rainfall[index],
                forecast_confidence=confidences[index],
            )
        )
    return ForecastClimateTimeline(source="sample_7_day_forecast", forecast_days=days)


def print_forecast_timeline(timeline) -> None:
    print("\nPestSense MVP Forecast Biological Simulation")
    print("=" * 56)
    print(f"Projected days: {len(timeline.projected_days)}")
    print("\nProjected Biological Timeline")
    print("-" * 56)
    for day in timeline.projected_days:
        print(f"\n{day.simulation_date.isoformat()}")
        print(f"  Crop stage: {format_value(day.projected_crop_state.current_stage)}")
        print(f"  Crop accumulated GDD: {day.projected_crop_state.accumulated_gdd:.2f}")
        print(f"  Simulation confidence: {day.simulation_confidence:.2f}")
        for pest_state in day.projected_pest_states:
            suitability = find_by_pest(day.projected_suitability_states, pest_state.pest_id)
            risk = find_by_pest(day.projected_risk_states, pest_state.pest_id)
            recommendation = find_recommendation(day.projected_recommendations, pest_state.pest_id)
            print(f"  Pest: {pest_state.pest_id}")
            print(f"    Stage: {format_value(pest_state.current_stage)}")
            print(f"    Pest GDD: {pest_state.accumulated_gdd:.2f}")
            if suitability:
                print(f"    Suitability: {suitability.overall_suitability:.2f}")
            if risk:
                print(f"    Risk: {risk.risk_score:.2f} ({format_value(risk.risk_level)})")
            if recommendation:
                print(f"    Recommendation: {recommendation.recommended_action}")
                print(f"    Timing: {format_window(recommendation.timing_window)}")

    print("\nOutbreak Windows")
    print("-" * 56)
    print_windows(timeline.outbreak_windows)
    print("\nIntervention Windows")
    print("-" * 56)
    print_windows(timeline.intervention_windows)
    print("\nConfidence Curve")
    print("-" * 56)
    for index, confidence in enumerate(timeline.confidence_curve, start=1):
        print(f"Day {index}: {confidence:.2f}")
    print("\nForecast Summary")
    print("-" * 56)
    print_list(timeline.summary)
    print()


def find_by_pest(states, pest_id: str):
    for state in states:
        if state.pest_id == pest_id:
            return state
    return None


def find_recommendation(recommendations, pest_id: str):
    for recommendation in recommendations:
        if recommendation.target_pest == pest_id:
            return recommendation
    return None


def format_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def format_window(window: Optional[TimeWindow]) -> str:
    if window is None:
        return "not projected"
    return f"{window.start.isoformat()} to {window.end.isoformat()}"


def print_windows(windows: Iterable[TimeWindow]) -> None:
    items = list(windows)
    if not items:
        print("No windows projected.")
        return
    for window in items:
        print(f"- {format_window(window)}")


def print_list(values: Iterable[str]) -> None:
    for value in values:
        print(f"- {value}")


if __name__ == "__main__":
    main()
