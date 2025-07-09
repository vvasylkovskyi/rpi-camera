import os

from fastapi import  APIRouter
from fastapi.responses import StreamingResponse, FileResponse

from rpi_camera.video_operations.rpi_camera import RpiCamera

model = "/usr/share/imx500-models/imx500_network_mobilenet_v2.rpk"

videos_router = APIRouter(prefix="/videos")

@videos_router.get("/start-recording")
def record_video():
    rpi_camera = RpiCamera()
    rpi_camera.start_recording()
    return {"status": "Recording started"}

@videos_router.get("/stop-recording")
def record_video():
    rpi_camera = RpiCamera()
    rpi_camera.stop_recording()
    return {"status": "Recording stopped"}


@videos_router.get("/stream")
def stream_live_jpeg_frames():
    rpi_camera = RpiCamera()
    rpi_camera.start_jpeg_camera()
    rpi_camera.start_recording()
    
    return StreamingResponse(
        rpi_camera.generate_live_jpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@videos_router.get("/get-recorded-mp4/{filename}")
def get_video_file(filename: str):
    file_path = f"/home/vvasylkovskyi/videos/{filename}"
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(path=file_path, media_type="video/mp4", filename=filename)