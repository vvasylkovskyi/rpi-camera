from fastapi import APIRouter
from rpi_camera.routes.health_check.controller import health_check_router
from rpi_camera.routes.videos.controller import videos_router


def create_router():
    router = APIRouter(prefix="/api/v1")

    router.include_router(health_check_router, tags=["Health"])
    router.include_router(videos_router, tags=["Video"])

    return router
