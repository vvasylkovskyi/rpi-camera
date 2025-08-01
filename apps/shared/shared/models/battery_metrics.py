from pydantic import BaseModel

class BatteryMetrics(BaseModel):
    charge_level: str
    temperature: str
    voltage: str
    current: str
    is_charging: bool

