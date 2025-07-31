import datetime
import os

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from shared.logger.logger import Logger
from shared.models.camera_control_event import WebRTCOffer

from camera.streaming_output import StreamingOutput
from webrtc.webrtc_streamer import PicameraVideoTrack, WebRTCStreamer


class Camera:
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
            main={"size": (640, 480), "format": "RGB888"} # Force 3 channels for RGB
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

    ## OLD, Uses HLS but has to high latency which is not practical for Camera
    # # output = PyavOutput("udp://44.217.93.156:4001", format="mpegts")
    # output = PyavOutput("udp://192.168.2.223:4001", format="mpegts")
    # encoder = H264Encoder(bitrate=2_000_000)
    # self.camera.start_recording(encoder, output)
        
    async def _start_webrtc_stream(self, webrtc_offer: WebRTCOffer):
        if self.is_recording:
            self.logger.warning("Cannot start WebRTC stream while recording")
            return None
        self.logger.info("Starting Camera...")
        encoder = H264Encoder(bitrate=2_000_000)
        self.camera.start_recording(encoder, self.output)
        self.logger.info("Camera started. ")
        self.logger.info("Starting WebRTC stream...")
        self.webrtc_streamer = WebRTCStreamer()
        picamera_video_track = PicameraVideoTrack(self.camera)
        answer_sdp = await self.webrtc_streamer.start(webrtc_offer.sdp, picamera_video_track)
        self.logger.info(f"WebRTC stream started with answer SDP: {answer_sdp}")
        return answer_sdp

    async def _stop_webrtc_stream(self):
        self.logger.info("Stopping WebRTC stream...")
        if hasattr(self, 'webrtc_streamer'):
            await self.webrtc_streamer.stop()
            self.logger.info("WebRTC stream stopped.")
    
        self.logger.info("Stopping Camera...")
        self.camera.stop_recording()
        self.logger.info("Camera stopped.")            
        
        
    ### OLD, Uses HLS but has to high latency which is not practical for Camera
    # # output = PyavOutput("udp://44.217.93.156:4001", format="mpegts")
    # output = PyavOutput("udp://192.168.2.223:4001", format="mpegts")
    # encoder = H264Encoder(bitrate=2_000_000)
    # self.camera.start_recording(encoder, output)
            
    async def start_webrtc_stream(self, webrtc_offer: WebRTCOffer):
        # if self.is_recording:
        #     self.logger.warning("Cannot start live stream while recording")
        #     return False

        self.logger.info("Starting live stream...")
        answer_sdp = await self._start_webrtc_stream(webrtc_offer)
        self.logger.info(f"Live stream started with answer SDP: {answer_sdp}")

        self.is_recording = True
        return answer_sdp

    async def stop_webrtc_stream(self):
        if not self.is_recording:
            self.logger.warning("No WebRTC stream in progress.")
            return False

        self.logger.info("Stopping WebRTC stream...")
        await self._stop_webrtc_stream()
        self.logger.info("Stopping Camera...")
        self.camera.stop_recording()
        self.logger.info("Camera stopped.")
        self.is_recording = False
        self.logger.info("WebRTC stream stopped.")
        return True
    
