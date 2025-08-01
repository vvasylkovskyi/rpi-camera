from abc import ABC, abstractmethod
import json

from pydantic import ValidationError
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.logger.logger import Logger


class BaseTopicHandler(ABC):
    def __init__(self, logger_name: str, mqtt_client_name: str):
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
    async def handle_command(self, payload: dict):
        """Handle the command with the parsed payload"""
        pass

    async def handle_incoming_message(self, topic: str, message: str):
        # try:
        #     request_model = self.get_request_model()
        #     print(">>> message: ", message, "request_model: ", request_model)
        #     data = json.loads(message)
        #     payload = request_model.model_validate(data)
        #     print(">> payload: ", payload)
        # except ValidationError as e:
        #     self.logger.error(f"Invalid {request_model.__name__} received '{message}': {e}")
        #     return
        
        data = json.loads(message)
        await self.handle_command(data)
