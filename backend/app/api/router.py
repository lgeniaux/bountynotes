from fastapi import APIRouter

from app.api.routers.sources import router as sources_router
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


router.include_router(sources_router)
