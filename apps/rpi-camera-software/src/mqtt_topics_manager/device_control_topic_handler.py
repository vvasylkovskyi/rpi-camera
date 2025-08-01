
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

    async def handle_command(self, data: DeviceControlRequestEvent):
        if data.action == DeviceControlAction.GET_HEALTH_CHECK:
            self.handle_get_health_check_event(data)
        elif data.action == DeviceControlAction.SHUTDOWN:
            self.logger.info("Device shutdown command received.")
            self.handle_shutdown_event(data)
            self.logger.info("Device is shutting down...")
        elif data.action == DeviceControlAction.RESTART:
            self.logger.info("Device restart command received.")
            self.handle_restart_event(data)
            self.logger.info("Device is restarting...")
        else:
            self.logger.error(f"Unknown command: {data.action}")

    def handle_get_health_check_event(self, payload: DeviceControlRequestEvent):
        self.logger.info("Getting device health check...")

        device = Device()
        device_health_info: DeviceMetrics = device.collect_metrics()
        self.logger.info("Device health check read successfully.")

        device_control_event = DeviceControlResponseEvent(
            health_check_info=device_health_info,
        )

        self.logger.info(f"Publishing device health info to: {self.get_topic()}/response")
        self.mqtt_client.publish(f"{self.get_topic()}/response", device_control_event.json())
        self.logger.info("Device health info published successfully.")

    def handle_shutdown_event(self, payload: DeviceControlRequestEvent):
        # Implement the logic to shutdown the device
        self.logger.info("Shutting down the device...")
        device = Device()
        device.shutdown_device()

    def handle_restart_event(self, payload: DeviceControlRequestEvent):
        # Implement the logic to restart the device
        self.logger.info("Restarting the device...")
        device = Device()
        device.reboot_device()