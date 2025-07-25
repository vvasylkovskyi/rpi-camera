from fastapi import APIRouter

from video_service_web.logger.logger import Logger
from video_service_web.ffmpeg.ffmpeg_service import FFmpegStreamingService
from video_service_web.clients.aws_mqtt_client import AwsMQTTClient
from video_service_web.models.camera_control_event import (
    CameraControlEvent,
    CameraAction,
)
from video_service_web.mqtt.topics import MQTTTopics
from video_service_web.mqtt.mqtt_clients import MQTTClients

videos_router = APIRouter(prefix="/video")
logger = Logger("videos_router")


@videos_router.get("/")
async def get_all_videos():
    logger.info("Received request to get all videos")
    return {"status": "All videos retrieved successfully"}


@videos_router.get("/start-streaming-service")
async def start_streaming_service():
    ffmpeg_service = FFmpegStreamingService()
    stream_url = f"/hls/{ffmpeg_service.STREAM_NAME}.m3u8"
    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    event = CameraControlEvent(action=CameraAction.START_LIVE_STREAM)
    mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())

    # Wait for 20 seconds to ensure the stream is available
    success = await ffmpeg_service.start_and_wait(20)

    if not success:
        return {
            "status": "error",
            "message": "Stream failed to become available in time",
        }

    return {
        "status": "Video streaming service started successfully",
        "stream_url": stream_url,
    }


@videos_router.get("/stop-streaming-service")
async def stop_streaming_service():
    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)
    ffmpeg_service = FFmpegStreamingService()
    ffmpeg_service.stop()
    event = CameraControlEvent(action=CameraAction.START_WEBRTC_STREAM)
    mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())
    ffmpeg_service.cleanup()
    return {
        "status": "Video streaming service stopped successfully",
    }
