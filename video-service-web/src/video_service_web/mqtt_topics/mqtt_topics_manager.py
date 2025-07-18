import os
import traceback
from video_service_web.logger.logger import Logger


class MqttTopicManager:
    def __init__(self):
        self.logger = Logger("MqttTopicManager")
        self.topic = os.environ.get("AWS_IOT_MQTT_TOPIC")
        self.topic_handlers = {self.topic: self.on_video_event_received}

    def handle_message(self, payload: bytes):
        try:
            message = payload.decode("utf-8")
            self.logger.info(f"Message received on topic '{self.topic}': {message}")

            handler = self.topic_handlers.get(self.topic)
            if handler:
                handler(message)
            else:
                self.logger.warn(f"No handler found for topic '{self.topic}'")

        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            self.logger.debug(traceback.format_exc())

    def on_video_event_received(self, message: str):
        self.logger.success(f"📹 Handling video event: {message}")
        # TODO: implement your actual business logic here
