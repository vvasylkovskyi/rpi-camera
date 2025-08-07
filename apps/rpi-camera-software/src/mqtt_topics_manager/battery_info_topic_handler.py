from shared.models.battery_info_event import BatteryAction, BatteryInfoRequestEvent, BatteryInfoResponseEvent
from shared.models.battery_metrics import BatteryMetrics
from shared.mqtt.mqtt_topics import MQTTTopics

from battery.battery_manager import BatteryManager
from mqtt_topics_manager.base_topic_handler import BaseTopicHandler


class BatteryInfoTopicHandler(BaseTopicHandler):
    def __init__(self, device_id: str):
        super().__init__("BatteryInfoTopicHandler", device_id)

    def get_request_model(self):
        return BatteryInfoRequestEvent

    def get_topic(self):
        return MQTTTopics.BATTERY_CONTROL.with_device(self.get_device_id())

    async def handle_command(self, payload: BatteryInfoRequestEvent):
        command = payload.action
        if command == BatteryAction.GET_HEALTH_CHECK:
            self.handle_read_battery_status_event(payload)
        else:
            self.logger.error(f"Unknown command: {command}")

    def handle_read_battery_status_event(self, payload: BatteryInfoRequestEvent):
        self.logger.info("Reading battery status...")
        
        battery_manager = BatteryManager()
        battery_metrics: BatteryMetrics = battery_manager.get_battery_info()
        
        self.logger.info("Battery status read successfully.")
        
        battery_info_event = BatteryInfoResponseEvent(
            battery_info=battery_metrics
        )
        
        self.logger.info(f"Publishing battery info to: {self.get_topic()}/response")
        self.mqtt_client.publish(f"{self.get_topic()}/response", battery_info_event.json())
        self.logger.info("Battery info published successfully.")
