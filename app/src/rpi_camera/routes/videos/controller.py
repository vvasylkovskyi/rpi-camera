import os

from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from rpi_camera.video_operations.rpi_camera import RpiCamera

model = "/usr/share/imx500-models/imx500_network_mobilenet_v2.rpk"

videos_router = APIRouter(prefix="/videos")

@videos_router.get("/record-video")
def record_video():
    rpi_camera = RpiCamera()
    rpi_camera.record_mp4()

@videos_router.get("/stream")
def stream_live_jpeg_frames(request: Request):
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "Connection": "close"
    }

    rpi_camera = RpiCamera()
    rpi_camera.start_jpeg_camera()
    
    return StreamingResponse(
        rpi_camera.generate_live_jpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers=headers
    )

@videos_router.get("/{filename}")
def get_video_file(filename: str):
    file_path = f"/home/vvasylkovskyi/videos/{filename}"
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(path=file_path, media_type="video/mp4", filename=filename)