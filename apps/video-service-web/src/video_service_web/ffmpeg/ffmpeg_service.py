import ffmpeg
import os
import signal
import asyncio
import glob
from subprocess import Popen
from video_service_web.logger.logger import Logger

logger = Logger("FFmpegStreamingService")


class FFmpegStreamingService:
    _instance = None

    HLS_DIR = os.getenv(
        "HLS_DIR", "/Users/vvasylkovskyi/git/rpi-camera/video-service-web/hls"
    )

    UDP_PORT = os.getenv("UDP_PORT", 4001)
    UDP_URL = os.getenv("UDP_URL", "localhost")

    STREAM_NAME = "stream"
    SEGMENT_TIME = 2
    PLAYLIST_SIZE = 5

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FFmpegStreamingService, cls).__new__(cls)
            cls._instance.process = None
        return cls._instance

    def start(self):
        if self.process:
            logger.warning("FFmpeg process already running.")
            return  # Early return if already started

        os.makedirs(self.HLS_DIR, exist_ok=True)

        output_manifest = os.path.join(self.HLS_DIR, f"{self.STREAM_NAME}.m3u8")
        segment_pattern = os.path.join(self.HLS_DIR, f"{self.STREAM_NAME}_%03d.ts")

        try:
            self.process: Popen = (
                ffmpeg.input(
                    f"udp://{self.UDP_URL}:{self.UDP_PORT}",
                    format="mpegts",
                    timeout=5000000,
                )
                .output(
                    output_manifest,
                    format="hls",
                    hls_time=self.SEGMENT_TIME,
                    hls_list_size=self.PLAYLIST_SIZE,
                    hls_flags="delete_segments",
                    hls_segment_filename=segment_pattern,
                )
                .global_args("-loglevel", "info")
                .run_async(pipe_stdin=True)
            )
            logger.success("FFmpeg streaming process started.")
        except Exception as e:
            logger.error(f"Failed to start FFmpeg: {e}")
            self.process = None

    async def start_and_wait(
        self, timeout_seconds: float = 5.0, poll_interval: float = 0.2
    ) -> bool:
        if not self.process:
            self.start()
        else:
            logger.info("FFmpeg process already running, skipping start.")

        manifest_path = os.path.join(self.HLS_DIR, f"{self.STREAM_NAME}.m3u8")

        waited = 0.0
        while not os.path.exists(manifest_path) and waited < timeout_seconds:
            await asyncio.sleep(poll_interval)
            waited += poll_interval

        if os.path.exists(manifest_path):
            logger.success("Stream manifest is now available.")
            return True
        else:
            logger.error("Timed out waiting for manifest to appear.")
            return False

    def stop(self):
        if not self.process:
            logger.info("FFmpeg process is not running.")
            return

        try:
            self.process.send_signal(signal.SIGINT)
            self.process.wait(timeout=5)
            logger.success("FFmpeg process stopped successfully.")
        except Exception as e:
            logger.error(f"Failed to stop FFmpeg: {e}")
        finally:
            self.process = None

    def cleanup(self):
        """Remove the manifest and all segment files."""
        manifest_path = os.path.join(self.HLS_DIR, f"{self.STREAM_NAME}.m3u8")
        segment_pattern = os.path.join(self.HLS_DIR, f"{self.STREAM_NAME}_*.ts")

        try:
            # Remove manifest file
            if os.path.exists(manifest_path):
                os.remove(manifest_path)
                logger.info(f"Removed manifest file: {manifest_path}")

            # Remove segment files
            segments = glob.glob(segment_pattern)
            for segment_file in segments:
                os.remove(segment_file)
            logger.info(f"Removed {len(segments)} segment files.")
        except Exception as e:
            logger.error(f"Failed to cleanup HLS files: {e}")
