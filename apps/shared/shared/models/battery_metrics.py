from pydantic import BaseModel

class BatteryMetrics(BaseModel):
    charge_level: int
    temperature: int
    voltage: int
    current: int
    is_charging: bool

