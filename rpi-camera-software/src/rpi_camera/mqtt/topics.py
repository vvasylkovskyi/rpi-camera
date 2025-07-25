from enum import Enum

class MQTTTopics(Enum):
    CAMERA_CONTROL = "raspberrypi/control"
    CAMERA_WEBCAM_STREAM = "raspberrypi/webrtc_stream"
    CAMERA_FEED = "raspberrypi/feed"
