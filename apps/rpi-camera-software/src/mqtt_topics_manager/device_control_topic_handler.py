from shared.models.device_control_event import (
    DeviceControlAction,
    DeviceControlRequestEvent,
    DeviceControlResponseEvent,
    DeviceHealthCheckInfo,
)
from shared.mqtt.mqtt_clients import MQTTClients
from shared.mqtt.mqtt_topics import MQTTTopics

from device.device import Device
from mqtt_topics_manager.base_topic_handler import BaseTopicHandler


class DeviceControlTopicHandler(BaseTopicHandler):
    def __init__(self):
        super().__init__("DeviceControlTopicHandler", MQTTClients.CAMERA.value)

    def get_request_model(self):
        return DeviceControlRequestEvent

    def get_topic(self):
        return MQTTTopics.DEVICE_CONTROL.value

    async def handle_command(self, command: str, payload):
        if command == DeviceControlAction.GET_HEALTH_CHECK.value:
            self.handle_get_health_check_event(payload)
        else:
            self.logger.error(f"Unknown command: {command}")

    def handle_get_health_check_event(self, payload: DeviceControlRequestEvent):
        self.logger.info("Getting device health check...")

        device = Device()
        device_health_info = device.collect_metrics()
        self.logger.info("Device health check read successfully.")

        device_control_event = DeviceControlResponseEvent(
            health_check_info=DeviceHealthCheckInfo(
                device_id=device_health_info.device_id,
                cpu_percent=device_health_info.cpu_percent,
                memory_percent=device_health_info.memory_percent,
                disk_percent=device_health_info.disk_percent,
                uptime_seconds=device_health_info.uptime_seconds
            )
        )

        self.logger.info(f"Publishing device health info to: {self.get_topic()}")
        self.mqtt_client.publish(self.get_topic(), device_control_event.json())
        self.logger.info("Device health info published successfully.")
