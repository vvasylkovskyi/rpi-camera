import asyncio
import signal
from rpi_camera.logger.logger import Logger
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from rpi_camera.logger.logger import Logger
from rpi_camera.mqtt_topics_manager.mqtt_topics_manager import MqttTopicManager
from rpi_camera.mqtt.rpi_camera_control_topic_handler import RpiCameraControlTopicHandler
from rpi_camera.mqtt.battery_info_topic_handler import BatteryInfoTopicHandler
from rpi_camera.mqtt.topics import MQTTTopics
from rpi_camera.mqtt.mqtt_clients import MQTTClients
from rpi_camera.battery_manager.battery_manager import BatteryManager

logger = Logger("main")

async def main():
    logger.info("Starting RPI Camera...")
    loop = asyncio.get_running_loop()
    mqtt_client = AwsMQTTClient(MQTTClients.CAMERA.value)
    topic_manager = MqttTopicManager(mqtt_client, loop)
    rpi_camera_control_topic_handler = RpiCameraControlTopicHandler()
    battery_info_topic_handler = BatteryInfoTopicHandler()
    battery_manager = BatteryManager()
    battery_manager.get_battery_info()
    try:
        logger.info("Starting MQTT client connection...")
        await mqtt_client.connect()
        logger.success("MQTT client connected successfully.")
        await topic_manager.subscribe_handler_to_topic(MQTTTopics.CAMERA_CONTROL.value, rpi_camera_control_topic_handler.handle_incoming_message)
        logger.info("Subscribed to camera control topic.")
        await topic_manager.subscribe_handler_to_topic(MQTTTopics.BATTERY_INFO.value, battery_info_topic_handler.handle_incoming_message)
        logger.info("Subscribed to battery info topic.")

        # Optionally, subscribe here or start message handling if implemented
        # await mqtt_client.subscribe("rpi-camera/control", on_video_event_received)
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