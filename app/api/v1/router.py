from fastapi import APIRouter

from app.api.v1.routes.analysis import router as analysis_router
from app.api.v1.routes.validation import router as validation_router
from app.api.v1.routes.profiles import router as profiles_router
from app.api.v1.routes.system import router as system_router

router = APIRouter(prefix="/api/v1")

router.include_router(system_router)
router.include_router(profiles_router)
router.include_router(analysis_router)
router.include_router(validation_router)