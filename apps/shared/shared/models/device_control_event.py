from enum import Enum

from pydantic import BaseModel
from shared.models.device_metrics import DeviceMetrics
from shared.models.generic_request_event import GenericRequestEvent

class DeviceControlAction(Enum):
    GET_HEALTH_CHECK = "get_health_check"
    SHUTDOWN = "shutdown"
    RESTART = "restart"

class DeviceControlRequestEvent(GenericRequestEvent):
    action: DeviceControlAction

class DeviceControlResponseEvent(BaseModel):
    health_check_info: DeviceMetrics

