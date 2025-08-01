from enum import Enum

from pydantic import BaseModel
from shared.models.device_metrics import DeviceMetrics

class DeviceControlAction(Enum):
    GET_HEALTH_CHECK = "get_health_check"

class DeviceControlRequestEvent(BaseModel):
    action: DeviceControlAction

class DeviceControlResponseEvent(BaseModel):
    health_check_info: DeviceMetrics

