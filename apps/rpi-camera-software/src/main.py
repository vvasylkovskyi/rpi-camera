import asyncio
import signal
from shared.logger.logger import Logger
from shared.clients.aws_mqtt_client import AwsMQTTClient
from mqtt_topics_manager.mqtt_topics_manager import MqttTopicManager
from mqtt_topics_manager.camera_control_topic_handler import CameraControlTopicHandler
from mqtt_topics_manager.battery_info_topic_handler import BatteryInfoTopicHandler
from mqtt_topics_manager.device_control_topic_handler import DeviceControlTopicHandler
from shared.mqtt.mqtt_topics import MQTTTopics
from shared.mqtt.mqtt_clients import MQTTClients
from battery.battery_manager import BatteryManager
from device.device import Device

logger = Logger("main")

async def main():
    logger.info("Starting Device...")

    device = Device()
    device.collect_metrics()
    battery_manager = BatteryManager()
    battery_manager.get_battery_info()
    
    logger.info("Starting MQTT and Camera Module...")
    
    mqtt_client = AwsMQTTClient(MQTTClients.CAMERA.value)
    loop = asyncio.get_running_loop()
    topic_manager = MqttTopicManager(mqtt_client, loop)
    
    device_health_check_topic_handler = DeviceControlTopicHandler()
    battery_info_topic_handler = BatteryInfoTopicHandler()
    rpi_camera_control_topic_handler = CameraControlTopicHandler()

    try:
        logger.info("Starting MQTT client connection...")
        await mqtt_client.connect()
        logger.success("MQTT client connected successfully.")
        await topic_manager.subscribe_handler_to_topic(MQTTTopics.DEVICE_CONTROL.value, device_health_check_topic_handler.handle_incoming_message)
        logger.info("Subscribed to device control topic.")
        await topic_manager.subscribe_handler_to_topic(MQTTTopics.BATTERY_CONTROL.value, battery_info_topic_handler.handle_incoming_message)
        logger.info("Subscribed to battery info topic.")
        await topic_manager.subscribe_handler_to_topic(MQTTTopics.CAMERA_CONTROL.value, rpi_camera_control_topic_handler.handle_incoming_message)
        logger.info("Subscribed to camera control topic.")

        logger.success("MQTT client subscribed to rpi-camera/control.")

        # Run until stopped, e.g. by Ctrl+C
        logger.info("Running MQTT client... Press Ctrl+C to exit.")
        stop_event = asyncio.Event()

        def shutdown_handler():
            logger.info("Shutdown signal received, stopping...")
            stop_event.set()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, shutdown_handler)
        loop.add_signal_handler(signal.SIGTERM, shutdown_handler)

        await stop_event.wait()

    except Exception as e:
        logger.error(f"Error in MQTT client: {e}")

    finally:
        logger.info("Disconnecting MQTT client...")
        try:
            await mqtt_client.disconnect()
            logger.success("MQTT client disconnected successfully.")
        except Exception as e:
            logger.error(f"MQTT client disconnect failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())