from enum import Enum

class MQTTTopics(Enum):
    CAMERA_CONTROL = "raspberrypi/control"
    CAMERA_FEED = "raspberrypi/feed"
