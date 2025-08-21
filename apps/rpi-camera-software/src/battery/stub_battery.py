from shared.logger.logger import Logger


class StubBattery:
    _instance = None
    logger = Logger("StubBattery")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_battery()
        return cls._instance

    def _init_battery(self):
        self.logger.warning(
            "StubBattery initialized, no real battery functionality available."
        )

    def get_energy_consumption(self):
        self.logger.warning(
            "Battery energy consumption not available (StubBattery used)"
        )
        return 0

    def get_status(self):
        self.logger.warning("Battery status not available (StubBattery used)")
        return {"battery": "unknown"}

    def get_charge_level(self):
        self.logger.warning("Battery charge level not available (StubBattery used)")
        return "N/A"

    def get_temperature(self):
        self.logger.warning("Battery temperature not available (StubBattery used)")
        return "N/A"

    def get_voltage(self):
        self.logger.warning("Battery voltage not available (StubBattery used)")
        return "N/A"

    def get_current(self):
        self.logger.warning("Battery current not available (StubBattery used)")
        return "N/A"
