import os

from rpi_camera.clients.aws_s3_client import S3Client
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, FileResponse

from rpi_camera.video_operations.rpi_camera import RpiCamera

model = "/usr/share/imx500-models/imx500_network_mobilenet_v2.rpk"

videos_router = APIRouter(prefix="/videos")


@videos_router.get("/start-recording")
def record_video():
    rpi_camera = RpiCamera()
    rpi_camera.record_mp4()


@videos_router.get("/stop-camera")
def stop_camera():
    rpi_camera = RpiCamera()
    rpi_camera.record_mp4()


@videos_router.get("/stream")
def stream_live_jpeg_frames(request: Request):
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "Connection": "close",
    }


@videos_router.get("/stop-recording")
def stop_recording_and_upload():
    rpi_camera = RpiCamera()
    filename = rpi_camera.stop_recording()
    if filename:
        s3 = S3Client(bucket_name="vvasylkovskyi-video-service-video-s3")
        s3_path = s3.upload_file(filename)
        return {
            "status": "Stopped and uploaded",
            "local_file": filename,
            "s3_path": s3_path,
        }
    return {"status": "Stopped", "file": filename}


# @videos_router.get("/stream")
# def stream_live_jpeg_frames():
#     rpi_camera = RpiCamera()
#     rpi_camera.start_jpeg_camera()
#     rpi_camera.start_recording()

#     return StreamingResponse(
#         rpi_camera.generate_live_jpeg_frames(),
#         media_type="multipart/x-mixed-replace; boundary=frame",
#     )


@videos_router.get("/get-recorded-mp4/{filename}")
def get_video_file(filename: str):
    file_path = f"/home/vvasylkovskyi/videos/{filename}"
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(path=file_path, media_type="video/mp4", filename=filename)


@videos_router.get("/list")
def list_mp4_files():
    video_dir = "/home/vvasylkovskyi/videos"
    if not os.path.exists(video_dir):
        return {"error": "Video directory not found"}

    mp4_files = [
        {
            "filename": f,
        }
        for f in os.listdir(video_dir)
        if f.endswith(".mp4") and os.path.isfile(os.path.join(video_dir, f))
    ]

    return {"videos": mp4_files}
