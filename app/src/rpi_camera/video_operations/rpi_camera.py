from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder, H264Encoder
from rpi_camera.video_operations.streaming_output import StreamingOutput
import time
import os
import datetime

import subprocess


class RpiCamera:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_camera()
        return cls._instance

    def _init_camera(self):
        self.camera = Picamera2()
        configuration = self.camera.create_video_configuration(
            main={"size": (640, 480)}
        )
        self.camera.configure(configuration)
        self.output = StreamingOutput()

    def record_mp4(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = f"/home/vvasylkovskyi/videos/recording_{timestamp}"
        filename_h264 = f"{base_path}.h264"
        filename_mp4 = f"{base_path}.mp4"

        os.makedirs(os.path.dirname(filename_h264), exist_ok=True)

        encoder = H264Encoder(bitrate=2_000_000)
        self.camera.start_recording(encoder, filename_h264)
        print(f"Recording started: {filename_h264}")

        time.sleep(10)

        self.camera.stop_recording()
        print("Recording stopped, converting to mp4...")

        # Convert to MP4 using ffmpeg
        subprocess.run(
            [
                "ffmpeg",
                "-framerate",
                "30",
                "-i",
                filename_h264,
                "-c",
                "copy",
                filename_mp4,
            ]
        )

        print(f"Video saved as: {filename_mp4}")

    def generate_live_jpeg_frames(self):
        while True:
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame

            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(1 / 30)  # 30 FPS

    def start_jpeg_camera(self):
        if not self.camera:
            raise RuntimeError("Camera is not started.")
        encoder = JpegEncoder()
        self.camera.start()
        self.camera.start_encoder(encoder, self.output)
