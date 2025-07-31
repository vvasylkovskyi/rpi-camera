from enum import Enum


class MQTTClients(Enum):
    CAMERA = "rpi-camera"
    TERMINAL = "rpi-terminal"
    WEB_SERVICE = "video-service-web"
