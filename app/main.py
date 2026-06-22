from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_router
from app.bootstrap.startup import startup
from app.core.container import container


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup / shutdown lifecycle.
    """
    startup()
    yield
    # future shutdown cleanup goes here
    # close db pools
    # flush queues
    # shutdown schedulers


app = FastAPI(
    title=container.settings.APP_NAME,
    version="1.0.0",
    description="AI-powered pest intelligence and predictive IPM platform.",
    lifespan=lifespan,

    # docs
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(api_router)