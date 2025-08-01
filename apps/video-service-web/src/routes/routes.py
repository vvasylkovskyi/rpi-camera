from fastapi import APIRouter
from routes.health_check.controller import health_check_router
from routes.videos.controller import videos_router
from routes.device.controller import device_router

def create_router():
    router = APIRouter(prefix="/api/v1")

    router.include_router(health_check_router, tags=["Health"])
    router.include_router(videos_router, tags=["Video"])
    router.include_router(device_router, tags=["Device"])
    
    return router
