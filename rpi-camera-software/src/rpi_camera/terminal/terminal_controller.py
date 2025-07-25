from rpi_camera.logger.logger import Logger  
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from rpi_camera.mqtt.topics import MQTTTopics
from rpi_camera.mqtt.mqtt_clients import MQTTClients
from rpi_camera.models.camera_control_event import CameraControlEvent, CameraAction

class TerminalController:
    def __init__(self):
        self.logger = Logger("Terminal")
        self.mqtt_client = AwsMQTTClient(MQTTClients.TERMINAL.value)

    def start(self):
        self._run_menu_loop()

    def _run_menu_loop(self):
        self.logger.info("Terminal controller started. Waiting for user input...")
        menu_text = (
            "\nPlease choose an option:\n"
            "1) Start Video\n"
            "2) Stop Video\n"
            "3) Start Live Stream\n"
            "4) Stop Live Stream\n"
            "Press Ctrl+C to quit. \n"
            "Enter choice [1-4]: "
        )
        while True:
            try:
                choice = input(menu_text).strip()
            except EOFError:
                self.logger.info("Input closed. Exiting terminal controller.")
                break

            if choice == "1":
                self.logger.info("User selected: Start Video")
                event = CameraControlEvent(action=CameraAction.START)
                self.mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())
            elif choice == "2":
                self.logger.info("User selected: Stop Video")
                event = CameraControlEvent(action=CameraAction.STOP)
                self.mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())
            elif choice == "3":
                self.logger.info("User selected: Start WebRTC Stream")
                event = CameraControlEvent(action=CameraAction.START_WEBRTC_STREAM)
                self.mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())
            elif choice == "4":
                self.logger.info("User selected: Stop WebRTC Stream")
                event = CameraControlEvent(action=CameraAction.STOP_WEBRTC_STREAM)
                self.mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())
            else:
                self.logger.info(f"Invalid option '{choice}'. Please enter 1, 2, 3, or 4.")
