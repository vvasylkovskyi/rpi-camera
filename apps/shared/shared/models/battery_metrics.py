from pydantic import BaseModel


class BatteryMetrics(BaseModel):
    charge_level: str
    temperature: str
    voltage: str
    current: str
    charging_status: str
    energy_consumption: str
