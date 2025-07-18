from datetime import datetime, timezone
import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from rpi_camera.clients.aws_s3_client import S3Client
from rpi_camera.models.video_event import VideoRecordingEvent
from rpi_camera.video_operations.rpi_camera import RpiCamera
from rpi_camera.logger.logger import Logger  

model = "/usr/share/imx500-models/imx500_network_mobilenet_v2.rpk"

videos_router = APIRouter(prefix="/videos")
logger = Logger("videos_router")  


@videos_router.get("/start-recording")
async def record_video():
    logger.info("Received request to start recording")
    rpi_camera = RpiCamera()
    status = rpi_camera.start_video()
    if not status:
        logger.warning("Attempt to start recording but already in progress")
        return {"status": "Recording already in progress."}
    logger.info("Recording started successfully")
    return {"status": "Recording started"}


@videos_router.get("/stop-recording")
async def stop_recording_and_upload():
    logger.info("Received request to stop recording")
    rpi_camera = RpiCamera()
    mqtt_client = AwsMQTTClient()

    filename = await rpi_camera.stop_video()

    if filename:
        logger.info(f"Recording stopped, file: {filename}")
        s3 = S3Client(bucket_name="vvasylkovskyi-video-service-video-s3")
        s3_path = s3.upload_file(filename)

        if s3_path is None:
            logger.error(f"Failed to upload {filename} to S3")
            return {"status": "Failed to upload to S3", "file": filename}

        event = VideoRecordingEvent(
            device_id=mqtt_client.get_device_id(),
            video_url=s3_path,
            # timestamp=datetime.now(timezone.utc),
        )

        await mqtt_client.publish(event.json())
        logger.info(f"Published video recording event for file {filename}")

        return {
            "status": "Stopped and uploaded",
            "local_file": filename,
            "s3_path": s3_path,
        }

    logger.warning("No recording in progress to stop")
    return {"status": "No recording in progress.", "file": filename}


@videos_router.get("/get-recorded-mp4/{filename}")
def get_video_file(filename: str):
    file_path = f"/home/vvasylkovskyi/videos/{filename}"
    logger.info(f"Request to get video file: {filename}")
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {"error": "File not found"}

    logger.info(f"Serving video file: {file_path}")
    return FileResponse(path=file_path, media_type="video/mp4", filename=filename)


@videos_router.get("/list")
def list_mp4_files():
    video_dir = "/home/vvasylkovskyi/videos"
    logger.info("Request to list recorded MP4 files")
    if not os.path.exists(video_dir):
        logger.error("Video directory not found")
        return {"error": "Video directory not found"}

    mp4_files = [
        {"filename": f}
        for f in os.listdir(video_dir)
        if f.endswith(".mp4") and os.path.isfile(os.path.join(video_dir, f))
    ]

    logger.info(f"Found {len(mp4_files)} MP4 files")
    return {"videos": mp4_files}
