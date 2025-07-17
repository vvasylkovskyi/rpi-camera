from fastapi import APIRouter

from video_service_web.logger.logger import Logger

videos_router = APIRouter(prefix="/video")
logger = Logger("videos_router")


@videos_router.get("/")
async def get_all_videos():
    logger.info("Received request to get all videos")
    return {"status": "All videos retrieved successfully"}
