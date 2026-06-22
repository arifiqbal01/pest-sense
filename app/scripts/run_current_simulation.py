from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.orchestrators import CurrentAnalysisWorkflow
from app.profiles import load_default_profiles
from app.shared.kernel import ClimateSnapshot
from app.shared.value_objects import DailyTemperature, GeoLocation, TimeWindow


def main() -> None:
    profiles = load_default_profiles()
    crop_profile = profiles.get_crop_profile("crop_cotton")
    pest_profile = profiles.get_pest_profile("pest_whitefly")
    result = CurrentAnalysisWorkflow(profiles).run(
        climate_snapshot=sample_climate_snapshot(),
        crop_profile=crop_profile,
        pest_profiles=[pest_profile],
        sowing_date=date(2026, 5, 1),
    )
    print_current_result(result)


def sample_climate_snapshot() -> ClimateSnapshot:
    return ClimateSnapshot(
        id="climate_snapshot_current_demo",
        timestamp=datetime(2026, 6, 1, 12, tzinfo=timezone.utc),
        location=GeoLocation(region="Zahir Pir", latitude=28.82, longitude=70.52),
        temperature=DailyTemperature(minimum=28, maximum=39, average=34),
        humidity=62,
        rainfall_mm=2,
        source="sample_current_simulation",
        confidence=0.91,
    )


def print_current_result(result) -> None:
    climate = result.climate_state
    crop = result.crop_state
    print("\nPestSense MVP Current Biological Simulation")
    print("=" * 52)
    print(f"Region: {climate.location.region}")
    print(f"Timestamp: {climate.timestamp.isoformat()}")
    print("\nClimate")
    print("-" * 52)
    current = climate.current_conditions
    print(f"Temperature: {current.temperature.minimum:.1f}-{current.temperature.maximum:.1f} C (avg {current.temperature.mean:.1f} C)")
    print(f"Humidity: {current.humidity:.1f}%")
    print(f"Rainfall: {current.rainfall_mm:.1f} mm")
    print(f"Daily GDD: {climate.degree_day.daily_value:.2f}")
    print(f"Accumulated GDD: {climate.accumulated_gdd:.2f}")
    print_list("Climate reasoning", climate.reasoning)

    print("\nCrop")
    print("-" * 52)
    print(f"Crop stage: {format_value(crop.current_stage)}")
    print(f"Stage duration: {crop.stage_duration_days} days")
    print(f"Development completion: {crop.accumulated_development:.2%}")
    print(f"Heat stress: {format_value(crop.stress_state.heat_stress)}")
    print(f"Water stress: {format_value(crop.stress_state.water_stress)}")
    print_list("Crop reasoning", crop.reasoning)

    for pest, suitability, risk, recommendation in zip(
        result.pest_states,
        result.suitability_states,
        result.risk_states,
        result.recommendations,
    ):
        print(f"\nPest: {pest.pest_id}")
        print("-" * 52)
        print(f"Lifecycle stage: {format_value(pest.current_stage)}")
        print(f"Pest accumulated GDD: {pest.accumulated_gdd:.2f}")
        print(f"Population pressure: {pest.population_pressure.level}")
        print(f"Suitability score: {suitability.overall_suitability:.2f}")
        print(f"Risk score: {risk.risk_score:.2f}")
        print(f"Risk level: {format_value(risk.risk_level)}")
        print(f"Recommendation: {recommendation.recommended_action}")
        print(f"Urgency: {format_value(recommendation.urgency)}")
        print(f"Timing window: {format_window(recommendation.timing_window)}")
        print_list("Risk reasoning", risk.reasoning)
        print_list("Recommendation reasoning", recommendation.reasoning)
    print()


def format_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def format_window(window: Optional[TimeWindow]) -> str:
    if window is None:
        return "not projected"
    return f"{window.start.isoformat()} to {window.end.isoformat()}"


def print_list(title: str, values: Iterable[str]) -> None:
    items = list(values)
    if not items:
        return
    print(f"{title}:")
    for item in items:
        print(f"  - {item}")


if __name__ == "__main__":
    main()
