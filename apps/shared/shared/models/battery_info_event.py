from enum import Enum
from pydantic import BaseModel
from shared.models.battery_metrics import BatteryMetrics
from shared.models.generic_request_event import GenericRequestEvent


class BatteryAction(Enum):
    GET_HEALTH_CHECK = "get_health_check"


class BatteryInfoRequestEvent(GenericRequestEvent):
    action: BatteryAction


class BatteryInfoResponseEvent(BaseModel):
    battery_info: BatteryMetrics
