from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class CameraAction(Enum):
    START = "start"
    STOP = "stop"
    START_LIVE_STREAM = "start_live_stream"
    STOP_LIVE_STREAM = "stop_live_stream"

class CameraControlEvent(BaseModel):
    action: CameraAction
