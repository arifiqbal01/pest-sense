# app/api/v1/routes/analysis.py
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_current_analysis_workflow,
    get_profile_registry,
    get_weather_query_service,
)
from app.api.v1.contracts.analysis import (
    CurrentAnalysisRequest,
    CurrentAnalysisResponse,
)
from app.profiles import ProfileResolver

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


@router.post(
    "/current",
    response_model=CurrentAnalysisResponse,
)
def current_analysis(
    request: CurrentAnalysisRequest,
    workflow=Depends(get_current_analysis_workflow),
    weather_query=Depends(get_weather_query_service),
    registry=Depends(get_profile_registry),
):
    resolver = ProfileResolver(registry)

    context = resolver.resolve_analysis_context(
        crop=request.crop,
        region=request.region,
        pests=request.pests,
    )

    weather_context = weather_query.get_weather_context(
        location=context.region.weather_location,
    )

    result = workflow.run(
        weather_context=weather_context,
        region_profile=context.region,
        crop_profile=context.crop,
        pest_profiles=context.pests,
    )

    return result