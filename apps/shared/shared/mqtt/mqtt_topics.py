from enum import Enum

class MQTTTopics(Enum):
    CAMERA_CONTROL = "raspberrypi/control"
    BATTERY_CONTROL = "raspberrypi/battery_control"
    DEVICE_CONTROL = "raspberrypi/device_control"
