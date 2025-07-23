import os
import traceback
import asyncio
from typing import Callable, Dict
from rpi_camera.logger.logger import Logger
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient


class MqttTopicManager:
    def __init__(self, mqtt_client: AwsMQTTClient):
        self.logger = Logger("MqttTopicManager")
        self.mqtt_client = mqtt_client
        self.topic_handlers: Dict[str, Callable[[str, str], None]] = {}

    async def subscribe_handler_to_topic(self, topic: str, handler: Callable[[str, str], None]):
        self.logger.info(f"Registering handler and subscribing to topic: {topic}")
        self.topic_handlers[topic] = handler

        def mqtt_callback(topic: str, payload: bytes, **kwargs):
            self.handle_message(topic, payload)

        await self.mqtt_client.subscribe(topic, mqtt_callback)

    def handle_message(self, topic: str, payload: bytes):
        try:
            message = payload.decode("utf-8")
            self.logger.info(f"Message received on topic '{topic}' \n Message: {message}")

            handler = self.topic_handlers.get(topic)
            if handler:
                handler(topic, message)
            else:
                self.logger.warn(f"No handler registered for topic '{topic}'")

        except Exception as e:
            self.logger.error(f"Error handling message on topic '{topic}': {e}")
            self.logger.debug(traceback.format_exc())
