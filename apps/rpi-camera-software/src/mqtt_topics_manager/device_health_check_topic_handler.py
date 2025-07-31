from shared.models.device_health_check_event import (
    DeviceHealthCheckAction,
    DeviceHealthCheckRequestEvent,
    DeviceHealthCheckResponseEvent,
)
from shared.mqtt.mqtt_clients import MQTTClients
from shared.mqtt.mqtt_topics import MQTTTopics

from device_health_checker.device_health_checker import DeviceHealthChecker
from mqtt_topics_manager.base_topic_handler import BaseTopicHandler


class DeviceHealthCheckTopicHandler(BaseTopicHandler):
    def __init__(self):
        super().__init__("DeviceHealthCheckTopicHandler", MQTTClients.CAMERA.value)

    def get_request_model(self):
        return DeviceHealthCheckRequestEvent

    def get_topic(self):
        return MQTTTopics.DEVICE_HEALTH_CHECK.value

    async def handle_command(self, command: str, payload):
        if command == DeviceHealthCheckAction.GET_HEALTH_CHECK.value:
            self.handle_get_health_check_event(payload)
        else:
            self.logger.error(f"Unknown command: {command}")

    def handle_get_health_check_event(self, payload: DeviceHealthCheckRequestEvent):
        self.logger.info("Getting device health check...")

        device_health_checker = DeviceHealthChecker()
        device_health_info = device_health_checker.get_device_health_info()
        self.logger.info("Device health check read successfully.")

        device_health_info_event = DeviceHealthCheckResponseEvent(
            device_id=device_health_info.device_id,
            cpu_percent=device_health_info.cpu_percent,
            memory_percent=device_health_info.memory_percent,
            disk_percent=device_health_info.disk_percent,
            uptime_seconds=device_health_info.uptime_seconds
        )

        self.logger.info(f"Publishing device health info to: {self.get_topic()}")
        self.mqtt_client.publish(self.get_topic(), device_health_info_event.json())
        self.logger.info("Device health info published successfully.")
