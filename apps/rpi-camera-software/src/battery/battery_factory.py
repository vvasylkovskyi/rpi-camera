from shared.logger.logger import Logger

class BatteryFactory:
    _instance = None
    logger = Logger("BatteryFactory")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.battery = cls._get_battery_instance()
        return cls._instance.battery

    @staticmethod
    def _get_battery_instance():
        """Returns an instance of the battery, either PiJuiceBattery or StubBattery."""
        try:
            from battery.pijuice_battery import PiJuiceBattery
            return PiJuiceBattery()
        except ModuleNotFoundError:
            from battery.stub_battery import StubBattery
            BatteryFactory.logger.warning("PiJuiceBattery not found, using StubBattery instead.")
            return StubBattery()
