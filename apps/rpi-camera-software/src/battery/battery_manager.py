
from shared.logger.logger import Logger

from shared.models.battery_metrics import BatteryMetrics
from battery.battery_factory import BatteryFactory

class BatteryManager:
    _instance = None
    logger = Logger("BatteryManager")
    battery = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.battery = BatteryFactory()
        return cls._instance

    def get_battery_info(self):
        battery_status = self.battery.get_status()

        battery_info = BatteryMetrics(
            charge_level=f"{self.battery.get_charge_level()}%",
            temperature=f"{self.battery.get_temperature()}°C",
            voltage=f"{self.battery.get_voltage()}mV",
            current=f"{self.battery.get_current()}mA",
            charging_status=battery_status["battery"],
        )

        self.logger.info(f"Battery Info: {battery_info}")

        return battery_info 