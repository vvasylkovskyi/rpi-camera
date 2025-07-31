from enum import Enum

from pydantic import BaseModel


class DeviceHealthCheckAction(Enum):
    GET_HEALTH_CHECK = "get_health_check"

class DeviceHealthCheckRequestEvent(BaseModel):
    action: DeviceHealthCheckAction

class DeviceHealthCheckResponseEvent(BaseModel):
    device_id: str
    cpu_percent: int
    memory_percent: int
    disk_percent: int
    uptime_seconds: float

