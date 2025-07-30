import asyncio

from jsonschema import ValidationError
from rpi_camera.video_operations.rpi_camera import RpiCamera
from rpi_camera.models.camera_control_event import CameraControlEvent, CameraAction, WebRTCOffer
from rpi_camera.logger.logger import Logger
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from rpi_camera.models.video_event import VideoRecordingEvent
from rpi_camera.mqtt.topics import MQTTTopics
from rpi_camera.mqtt.mqtt_clients import MQTTClients
from rpi_camera.clients.aws_s3_client import S3Client
from rpi_camera.battery_manager.battery_manager import BatteryManager
from rpi_camera.models.battery_info_event import BatteryInfoRequestEvent, BatteryAction, BatteryInfoResponseEvent

class BatteryInfoTopicHandler:
    def __init__(self, ):
        self.logger = Logger("BatteryInfoTopicHandler")
        self.rpi_camera = RpiCamera()
        self.mqtt_client = AwsMQTTClient(MQTTClients.CAMERA.value)

    async def handle_incoming_message(self, topic: str, message: str):
        try:
            # Validate/parse the incoming payload into the BatteryInfoRequestEvent model
            payload: BatteryInfoRequestEvent = BatteryInfoRequestEvent.parse_raw(message)
        except ValidationError as e:
            self.logger.error(f"Invalid BatteryInfoRequestEvent received '{message}': {e}")
            return  # Early exit on invalid data

        command = payload.action.value

        if command == BatteryAction.READ_STATUS.value:
            self.handle_read_battery_status_event(payload)
        else:
            self.logger.error(f"Unknown command: {command}")

    def handle_read_battery_status_event(self, payload: BatteryInfoRequestEvent):
        self.logger.info(f"Reading battery status...")
        # Implement the logic to read the battery status
        
        battery_manager = BatteryManager()
        battery_info = battery_manager.get_battery_info()
        
        self.logger.info("Battery status read successfully.")
        
        battery_info_event = BatteryInfoResponseEvent(
            charge_level=battery_info.charge_level,
            temperature=battery_info.temperature,
            voltage=battery_info.voltage,
            current=battery_info.current,
            is_charging=battery_info.is_charging
        )
        
        self.logger.info(f"Publishing battery info to: {MQTTTopics.BATTERY_INFO.value}")
        self.mqtt_client.publish(MQTTTopics.BATTERY_INFO.value, battery_info_event.json())
        self.logger.info("Battery info published successfully.")