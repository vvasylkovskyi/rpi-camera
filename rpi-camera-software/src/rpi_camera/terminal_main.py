import asyncio
from rpi_camera.logger.logger import Logger
from rpi_camera.terminal.terminal_controller import TerminalController  # your TerminalController class
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from rpi_camera.mqtt.mqtt_clients import MQTTClients

logger = Logger("TerminalRunner")

async def main():
    mqtt_client = AwsMQTTClient(MQTTClients.TERMINAL.value)  
    await mqtt_client.connect()  # Ensure the MQTT client is connected
    terminal_controller = TerminalController()
    terminal_controller.start()

    logger.info("Terminal Controller started. Press Ctrl+C to quit.")


if __name__ == "__main__":
    asyncio.run(main())
