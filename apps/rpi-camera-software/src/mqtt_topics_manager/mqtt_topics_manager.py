import asyncio
import traceback
from typing import Callable, Dict

from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.logger.logger import Logger


class MqttTopicManager:
    def __init__(self, mqtt_client: AwsMQTTClient, loop: asyncio.AbstractEventLoop):
        self.logger = Logger("MqttTopicManager")
        self.mqtt_client = mqtt_client
        self.loop = loop
        self.topic_handlers: Dict[str, Callable[[str, str], None]] = {}

    async def subscribe_handler_to_topic(self, topic: str, handler: Callable[[str, str], None]):
        self.logger.info(f"Registering handler and subscribing to topic: {topic}")
        self.topic_handlers[topic] = handler

        def mqtt_callback(topic: str, payload: bytes, **kwargs):
            self.loop.call_soon_threadsafe(
                asyncio.create_task, self._async_handle_message(topic, payload)
            )

        await self.mqtt_client.subscribe(topic, mqtt_callback)

    async def _async_handle_message(self, topic: str, payload: bytes):
        try:
            message = payload.decode("utf-8")
            self.logger.info(f"Message received on topic '{topic}' \n Message: {message}")
            handler = self.topic_handlers.get(topic)
            if handler:
                await handler(topic, message)
            else:
                self.logger.warn(f"No handler registered for topic '{topic}'")
        except Exception as e:
            self.logger.error(f"Error handling message on topic '{topic}': {e}")
            self.logger.debug(traceback.format_exc())
