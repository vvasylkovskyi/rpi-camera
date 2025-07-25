from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CameraAction(Enum):
    START = "start"
    STOP = "stop"
    START_WEBRTC_STREAM = "start_webrtc_stream"
<<<<<<< HEAD
    START_WEBRTC_STREAM_ANSWER = "start_webrtc_stream_answer"
    STOP_WEBRTC_STREAM = "stop_webrtc_stream"

class WebRTCOffer(BaseModel):
    type: str
    sdp: str
=======
    STOP_WEBRTC_STREAM = "stop_webrtc_stream"


class WebRTCOffer(BaseModel):
    type: str
    sdp: str

>>>>>>> f0114d1 (Implemented Web RTC MQTT exchange)

class CameraControlEvent(BaseModel):
    action: CameraAction
    webrtc_offer: Optional[WebRTCOffer] = None
<<<<<<< HEAD
    webrtc_answer: Optional[str] = None

=======
>>>>>>> f0114d1 (Implemented Web RTC MQTT exchange)
