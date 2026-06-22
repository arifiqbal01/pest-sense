from app.core.container import container


def get_profile_registry():
    return container.profile_registry


def get_weather_query_service():
    return container.weather_query_service


def get_current_analysis_workflow():
    return container.current_analysis_workflow


def get_forecast_simulation_engine():
    return container.forecast_simulation_engine


def get_validation_workflow():
    return container.validation_workflow