from enum import Enum

from pydantic import BaseModel

class DeviceHealthCheckInfo(BaseModel):
    cpu_percent: int
    memory_percent: int
    disk_percent: int
    uptime_seconds: float
    device_id: str

class DeviceControlAction(Enum):
    GET_HEALTH_CHECK = "get_health_check"

class DeviceControlRequestEvent(BaseModel):
    action: DeviceControlAction

class DeviceControlResponseEvent(BaseModel):
    health_check_info: DeviceHealthCheckInfo

