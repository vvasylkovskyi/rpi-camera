import asyncio
import signal
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from rpi_camera.logger.logger import Logger

logger = Logger("main")

async def main():
    mqtt_client = AwsMQTTClient()
    
    try:
        logger.info("Starting MQTT client connection...")
        await mqtt_client.connect()
        logger.success("MQTT client connected successfully.")

        # Optionally, subscribe here or start message handling if implemented
        # await mqtt_client.subscribe()

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
