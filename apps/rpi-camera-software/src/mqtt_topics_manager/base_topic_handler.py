from abc import ABC, abstractmethod
import json

from pydantic import ValidationError
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.logger.logger import Logger
from shared.mqtt.mqtt_clients import MQTTClients


class BaseTopicHandler(ABC):
    def __init__(self, logger_name: str, device_id: str):
        self.device_id = device_id
        mqtt_client_name = MQTTClients.DEVICE.with_device(device_id)
        self.logger = Logger(logger_name)
        self.mqtt_client = AwsMQTTClient(mqtt_client_name)

    @abstractmethod
    def get_request_model(self):
        """Return the Pydantic model class to parse incoming messages"""
        pass

    @abstractmethod
    def get_topic(self) -> str:
        """Return the MQTT topic for publishing responses"""
        pass

    @abstractmethod
    async def handle_command(self, payload):
        """Handle the command with the parsed payload"""
        pass

    async def handle_incoming_message(self, topic: str, message: str):
        try:
            request_model = self.get_request_model()
            payload = request_model.validate(json.loads(message)) # Not sure why double json.loads is needed, but it seems to be the case in the original code
            await self.handle_command(payload)
        except ValidationError as e:
            self.logger.error(f"Invalid {request_model.__name__} received '{message}': {e}")
            return

    def get_device_id(self) -> str:
        return self.device_id