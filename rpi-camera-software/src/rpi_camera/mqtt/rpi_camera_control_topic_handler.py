import asyncio

from jsonschema import ValidationError
from rpi_camera.video_operations.rpi_camera import RpiCamera
from rpi_camera.models.camera_control_event import CameraControlEvent, CameraAction, WebRTCOffer
from rpi_camera.logger.logger import Logger
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from rpi_camera.models.video_event import VideoRecordingEvent
from rpi_camera.mqtt.topics import MQTTTopics
from rpi_camera.mqtt.mqtt_clients import MQTTClients
from rpi_camera.clients.aws_s3_client import S3Client

class RpiCameraControlTopicHandler:
    def __init__(self, ):
        self.logger = Logger("RpiCameraControlTopicHandler")
        self.rpi_camera = RpiCamera()
        self.mqtt_client = AwsMQTTClient(MQTTClients.CAMERA.value)

    async def handle_incoming_message(self, topic: str, message: str):
        try:
            # Validate/parse the incoming payload into the CameraControlEvent model
            payload: CameraControlEvent = CameraControlEvent.parse_raw(message)
        except ValidationError as e:
            self.logger.error(f"Invalid CameraControlEvent received '{message}': {e}")
            return  # Early exit on invalid data

        command = payload.action.value
        
        if command == CameraAction.START.value:
            self.handle_start_video_event()
        elif command == CameraAction.STOP.value:
            self.handle_stop_video_event()
        elif command == CameraAction.START_WEBRTC_STREAM.value:
            webrtc_offer = payload.webrtc_offer
            await self.handle_start_webrtc_stream_event(webrtc_offer)
        elif command == CameraAction.STOP_WEBRTC_STREAM.value:
            await self.handle_stop_webrtc_stream_event()
        else:
            self.logger.error(f"Unknown command: {command}")
                    
    def handle_start_video_event(self):
        self.rpi_camera.start_video()
        self.logger.info("Camera video started.")
                    
    def handle_stop_video_event(self):
        filename = self.rpi_camera.stop_video()
        self.logger.info(f"Camera video stopped, file: {filename}")
        if filename:
            event = VideoRecordingEvent(
                device_id=self.mqtt_client.get_device_id(),
                video_url=filename,
                # timestamp=datetime.now(timezone.utc),
            )

            self.mqtt_client.publish(MQTTTopics.CAMERA_FEED.value, event.json())
            
            s3 = S3Client(bucket_name="vvasylkovskyi-video-service-video-s3")
            s3_path = s3.upload_file(filename)
            
            self.logger.info(f"Published video recording event for file {filename}")
            
            if s3_path is None:
                self.logger.error(f"Failed to upload {filename} to S3")
                return False

    async def handle_start_webrtc_stream_event(self, webrtc_offer: WebRTCOffer):
        answer_sdp = await self.rpi_camera.start_webrtc_stream(webrtc_offer)
        if not answer_sdp:
            self.logger.error("Failed to start WebRTC stream.")
            return
        
        event = CameraControlEvent(
            action=CameraAction.START_WEBRTC_STREAM_ANSWER,
            webrtc_answer=answer_sdp
        )
        self.logger.info(f"Publishing WebRTC stream answer to: {MQTTTopics.CAMERA_WEBCAM_STREAM.value}")
        self.mqtt_client.publish(MQTTTopics.CAMERA_WEBCAM_STREAM.value, event.json())
        self.logger.info("Camera WebRTC stream started.")

    async def handle_stop_webrtc_stream_event(self):
        await self.rpi_camera.stop_webrtc_stream()
        self.logger.info("Camera WebRTC stream stopped.")
