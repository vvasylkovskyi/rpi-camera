from pydantic import BaseModel

class DeviceMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    uptime_seconds: float
    device_id: str