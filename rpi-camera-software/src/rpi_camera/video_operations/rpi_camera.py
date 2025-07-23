from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder, H264Encoder
from rpi_camera.video_operations.streaming_output import StreamingOutput
import time
import os
import datetime
from rpi_camera.logger.logger import Logger 
from picamera2.outputs import FfmpegOutput

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
        # self.camera.start()
        self.logger.info("Camera started.")
        
        # Threading utils
        # self.stop_event = asyncio.Event()
        self.is_recording = False
        self.last_recorded_file_path = None

    def start_video(self):
        if self.is_recording:
            self.logger.warning("Already recording")
            return False

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = f"/home/vvasylkovskyi/videos/recording_{timestamp}"
        filename_mp4 = f"{base_path}.mp4"
        ffmpeg_output = FfmpegOutput(filename_mp4)

        os.makedirs(os.path.dirname(filename_mp4), exist_ok=True)

        encoder = H264Encoder(bitrate=2_000_000)
        self.camera.start_recording(encoder, ffmpeg_output)
        self.logger.info(f"Recording started: {filename_mp4}")
        self.last_recorded_file_path = base_path

        self.is_recording = True
        self.logger.info("Recording task started.")
        return True

    def stop_video(self):
        if self.is_recording:
            self.logger.info("Stopping video...")
            self.camera.stop_recording()
            self.is_recording = False
            filename_mp4 = f"{self.last_recorded_file_path}.mp4"
            self.logger.info(f"Recording stopped, file: {filename_mp4}")
            # await asyncio.sleep(3)  # Ensure file is fully written
            # s3 = S3Client(bucket_name="vvasylkovskyi-video-service-video-s3")
            # s3_path = s3.upload_file(filename_mp4)

            # if s3_path is None:
            #     self.logger.error(f"Failed to upload {filename_mp4} to S3")
            #     return False


            # self.logger.info(f"Published video recording event for file {filename_mp4}")

            return filename_mp4
        else:
            self.logger.warning("No recording in progress.")
            return None

    def start_live_stream(self):
        if self.is_recording:
            self.logger.warning("Cannot start live stream while recording")
            return False

        self.logger.info("Starting live stream...")
        # self.camera.start_encoder(JpegEncoder(), self.output)
        self.logger.info("Live stream started.")
        return True

    def stop_live_stream(self):
        if not self.is_recording:
            self.logger.warning("No live stream in progress.")
            return False

        self.logger.info("Stopping live stream...")
        # self.camera.stop_encoder()
        self.logger.info("Live stream stopped.")
        return True
    
    # def generate_live_jpeg_frames(self):
    #     self.logger.info("Starting JPEG frame generator...")
    #     while True:
    #         with self.output.condition:
    #             self.output.condition.wait()
    #             frame = self.output.frame

    #         yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
    #         time.sleep(1 / 30)  # 30 FPS

    # def start_jpeg_camera(self):
    #     if not self.camera:
    #         self.logger.error("Camera is not started.")
    #         raise RuntimeError("Camera is not started.")
    #     encoder = JpegEncoder()
    #     self.camera.start()
    #     self.camera.start_encoder(encoder, self.output)
    #     self.logger.info("JPEG camera started.")
