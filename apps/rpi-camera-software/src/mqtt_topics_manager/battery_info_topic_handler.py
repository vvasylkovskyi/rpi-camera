from shared.models.battery_info_event import BatteryAction, BatteryInfoRequestEvent, BatteryInfoResponseEvent
from shared.models.battery_metrics import BatteryMetrics
from shared.mqtt.mqtt_clients import MQTTClients
from shared.mqtt.mqtt_topics import MQTTTopics

from battery_manager.battery_manager import BatteryManager
from mqtt_topics_manager.base_topic_handler import BaseTopicHandler


class BatteryInfoTopicHandler(BaseTopicHandler):
    def __init__(self):
        super().__init__("BatteryInfoTopicHandler", MQTTClients.CAMERA.value)

    def get_request_model(self):
        return BatteryInfoRequestEvent

    def get_topic(self):
        return MQTTTopics.BATTERY_INFO.value

    async def handle_command(self, payload: BatteryInfoRequestEvent):
        command = payload.action
        if command == BatteryAction.READ_STATUS.value:
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
        
        self.logger.info(f"Publishing battery info to: {self.get_topic()}")
        self.mqtt_client.publish(self.get_topic(), battery_info_event.json())
        self.logger.info("Battery info published successfully.")
