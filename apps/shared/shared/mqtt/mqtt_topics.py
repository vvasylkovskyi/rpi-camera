from enum import Enum

class MQTTTopics(Enum):
    CAMERA_CONTROL = "homie/raspberrypi/camera/control/set"
    BATTERY_CONTROL = "homie/raspberrypi/battery/control/set"
    DEVICE_CONTROL = "homie/raspberrypi/device/control/set"

    BATTERY_LEVEL = "homie/raspberrypi/battery/level"
    CAMERA_STATUS = "homie/raspberrypi/camera/status"
    DEVICE_STATUS = "homie/raspberrypi/device/status"