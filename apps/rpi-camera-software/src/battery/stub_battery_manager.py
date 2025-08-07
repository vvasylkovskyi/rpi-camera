# battery_manager/stub_battery_manager.py

from shared.logger.logger import Logger
from shared.models.battery_metrics import BatteryMetrics

class StubBattery:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = Logger("StubBatteryManager")
        return cls._instance

    def get_battery_info(self):
        self.logger.warning("Battery info not available (StubBatteryManager used)")
        return BatteryMetrics(
            charge_level="N/A",
            temperature="N/A",
            voltage="N/A",
            current="N/A",
            charging_status="unknown"
        )
