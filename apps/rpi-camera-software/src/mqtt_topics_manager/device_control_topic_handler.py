import json

from shared.models.device_control_event import (
    DeviceControlAction,
    DeviceControlRequestEvent,
    DeviceControlResponseEvent,
)
from shared.models.device_metrics import DeviceMetrics
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

    async def handle_command(self, payload: str):
        # print(">>> payload: ", payload)
        # data: DeviceControlRequestEvent = DeviceControlRequestEvent.model_validate(payload)
        data = json.loads(payload)
        if data["action"] == DeviceControlAction.GET_HEALTH_CHECK.value:
            self.handle_get_health_check_event(data)
        else:
            self.logger.error(f"Unknown command: {data['action']}")

    def handle_get_health_check_event(self, payload: DeviceControlRequestEvent):
        self.logger.info("Getting device health check...")

        device = Device()
        device_health_info: DeviceMetrics = device.collect_metrics()
        self.logger.info("Device health check read successfully.")

        device_control_event = DeviceControlResponseEvent(
            health_check_info=device_health_info,
        )

        self.logger.info(f"Publishing device health info to: {self.get_topic()}")
        self.mqtt_client.publish(f"{self.get_topic()}/response", device_control_event.json())
        self.logger.info("Device health info published successfully.")
