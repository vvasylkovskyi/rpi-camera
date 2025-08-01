from enum import Enum
from pydantic import BaseModel
from shared.models.battery_metrics import BatteryMetrics

class BatteryAction(Enum):
    GET_HEALTH_CHECK = "get_health_check"

class BatteryInfoRequestEvent(BaseModel):
    action: BatteryAction

class BatteryInfoResponseEvent(BatteryMetrics):
    battery_info: BatteryMetrics

