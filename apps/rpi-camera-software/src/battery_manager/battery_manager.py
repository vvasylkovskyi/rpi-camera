
from shared.logger.logger import Logger

from pijuice_battery.pijuice_battery import PiJuiceBattery
from shared.models.battery_metrics import BatteryMetrics


class BatteryManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = Logger("BatteryManager")
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        self.battery = PiJuiceBattery()
        self.logger = Logger("BatteryManager")
        
    def get_battery_info(self):
        battery_status = self.battery.get_status()
        is_charging = battery_status["battery"] == "CHARGING_FROM_5V_IO" or battery_status["battery"] == "CHARGING_FROM_IN"

        battery_info = BatteryMetrics(
            charge_level=self.battery.get_charge_level(),
            temperature=self.battery.get_temperature(),
            voltage=self.battery.get_voltage(),
            current=self.battery.get_current(),
            is_charging=is_charging,
        )

        self.logger.info(f"Battery Info: {battery_info}")

        return battery_info 