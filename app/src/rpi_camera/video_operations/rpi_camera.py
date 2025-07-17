from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder, H264Encoder
from rpi_camera.video_operations.streaming_output import StreamingOutput
import time
import os
import datetime
import asyncio
from rpi_camera.logger.logger import Logger 

class RpiCamera:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = Logger("RpiCamera")
            cls._instance._init_camera()
        return cls._instance

    def _init_camera(self):
        self.logger.info("Initializing camera...")
        self.camera = Picamera2()
        configuration = self.camera.create_video_configuration(
            main={"size": (640, 480)}
        )
        self.camera.configure(configuration)
        self.encoder = None
        self.output = StreamingOutput()
        self.camera.start()  # Start once for both
        self.logger.info("Camera started.")

        # Threading utils
        self.stop_event = asyncio.Event()
        self.recording_task = None
        self.last_recorded_file_path = None

    def start_recording(self):
        if self.recording_task:
            self.logger.warning("Already recording")
            return False

        self.recording_task = asyncio.create_task(self._record_worker())
        self.logger.info("Recording task started.")
        return True

    async def _record_worker(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = f"/home/vvasylkovskyi/videos/recording_{timestamp}"
        filename_h264 = f"{base_path}.h264"
        filename_mp4 = f"{base_path}.mp4"

        os.makedirs(os.path.dirname(filename_h264), exist_ok=True)

        encoder = H264Encoder(bitrate=2_000_000)
        self.camera.start_recording(encoder, filename_h264)
        self.logger.info(f"Recording started: {filename_h264}")

        while not self.stop_event.is_set():
            await asyncio.sleep(1)

        self.last_recorded_file_path = base_path
        self.logger.info(f"Recording stopped. Filename saved as: {self.last_recorded_file_path}")

    async def convert_to_mp4(self):
        filename_h264 = f"{self.last_recorded_file_path}.h264"
        filename_mp4 = f"{self.last_recorded_file_path}.mp4"

        self.logger.info(f"Converting {filename_h264} to MP4 format...")
        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-framerate", "30",
            "-i", filename_h264,
            "-c", "copy",
            filename_mp4,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            self.logger.error(f"FFmpeg error: {stderr.decode()}")
            raise RuntimeError("Failed to convert video")
        
        self.logger.info(f"FFmpeg success: {stdout.decode()}")

    async def stop_recording(self):
        if self.recording_task:
            self.logger.info("Stopping recording...")
            self.stop_event.set()
            await self.recording_task  # Wait for graceful finish
            self.recording_task = None
            await self.convert_to_mp4()
            self.logger.info("Recording stopped and converted.")
            return f"{self.last_recorded_file_path}.mp4"
        else:
            self.logger.warning("No recording in progress.")
            return None

    def generate_live_jpeg_frames(self):
        self.logger.info("Starting JPEG frame generator...")
        while True:
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame

            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(1 / 30)  # 30 FPS

    def start_jpeg_camera(self):
        if not self.camera:
            self.logger.error("Camera is not started.")
            raise RuntimeError("Camera is not started.")
        encoder = JpegEncoder()
        self.camera.start()
        self.camera.start_encoder(encoder, self.output)
        self.logger.info("JPEG camera started.")
