from shared.clients.aws_s3_client import S3Client
from shared.models.camera_control_event import CameraAction, CameraControlEvent, WebRTCOffer
from shared.models.video_event import VideoRecordingEvent
from shared.mqtt.mqtt_clients import MQTTClients
from shared.mqtt.mqtt_topics import MQTTTopics

from camera.camera_factory import CameraFactory
from mqtt_topics_manager.base_topic_handler import BaseTopicHandler


class CameraControlTopicHandler(BaseTopicHandler):
    def __init__(self):
        super().__init__("CameraControlTopicHandler", MQTTClients.CAMERA.value)
        self.camera = CameraFactory()

    def get_request_model(self):
        return CameraControlEvent

    def get_topic(self):
        # This handler publishes to multiple topics depending on event type,
        # So just return None or override publish logic.
        return None

    async def handle_command(self, payload: CameraControlEvent):
        command = payload.action
        if command == CameraAction.START:
            self.handle_start_video_event()
        elif command == CameraAction.STOP:
            self.handle_stop_video_event()
        elif command == CameraAction.START_WEBRTC_STREAM:
            webrtc_offer = payload.webrtc_offer
            await self.handle_start_webrtc_stream_event(webrtc_offer)
        elif command == CameraAction.STOP_WEBRTC_STREAM:
            await self.handle_stop_webrtc_stream_event()
        else:
            self.logger.error(f"Unknown command: {command}")

    def handle_start_video_event(self):
        self.camera.start_video()
        self.logger.info("Camera video started.")

    def handle_stop_video_event(self):
        filename = self.camera.stop_video()
        self.logger.info(f"Camera video stopped, file: {filename}")
        if filename:
            event = VideoRecordingEvent(
                device_id=self.mqtt_client.get_device_id(),
                video_url=filename,
            )

            self.mqtt_client.publish(MQTTTopics.CAMERA_FEED.value, event.json())
            
            s3 = S3Client(bucket_name="vvasylkovskyi-video-service-video-s3")
            s3_path = s3.upload_file(filename)
            
            self.logger.info(f"Published video recording event for file {filename}")
            
            if s3_path is None:
                self.logger.error(f"Failed to upload {filename} to S3")
                return False

    async def handle_start_webrtc_stream_event(self, webrtc_offer: WebRTCOffer):
        answer_sdp = await self.camera.start_webrtc_stream(webrtc_offer)
        if not answer_sdp:
            self.logger.error("Failed to start WebRTC stream.")
            return
        
        event = CameraControlEvent(
            action=CameraAction.START_WEBRTC_STREAM_ANSWER,
            webrtc_answer=answer_sdp
        )
        self.logger.info(f"Publishing WebRTC stream answer to: {MQTTTopics.CAMERA_CONTROL.value}/response")
        self.mqtt_client.publish(f"{MQTTTopics.CAMERA_CONTROL.value}/response", event.json())
        self.logger.info("Camera WebRTC stream started.")

    async def handle_stop_webrtc_stream_event(self):
        await self.camera.stop_webrtc_stream()
        self.logger.info("Camera WebRTC stream stopped.")
