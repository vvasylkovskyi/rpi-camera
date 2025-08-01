from enum import Enum
from pydantic import BaseModel
from shared.models.battery_metrics import BatteryMetrics

class BatteryAction(Enum):
    READ_STATUS = "read_status"

class BatteryInfoRequestEvent(BaseModel):
    action: BatteryAction

class BatteryInfoResponseEvent(BatteryMetrics):
    battery_info: BatteryMetrics

