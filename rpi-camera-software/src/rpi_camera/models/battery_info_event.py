from enum import Enum
from pydantic import BaseModel

class BatteryAction(Enum):
    READ_STATUS = "read_status"

class BatteryInfoRequestEvent(BaseModel):
    action: BatteryAction

class BatteryInfoResponseEvent(BaseModel):
    charge_level: int
    temperature: int
    voltage: int
    current: int
    is_charging: bool

