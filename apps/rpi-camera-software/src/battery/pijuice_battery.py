from pijuice import (
    PiJuice,
)  # https://github.com/PiSupply/PiJuice/blob/master/Software/Source/pijuice.py
from shared.logger.logger import Logger


# API Docs - https://github.com/PiSupply/PiJuice/tree/master/Software#i2c-command-api
class PiJuiceBattery:
    _instance = None
    logger = Logger("PiJuiceBattery")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_battery()

        return cls._instance

    def _init_battery(self):
        self.pijuice = PiJuice(1, 0x14)  # Instantiate PiJuice interface object
        self.logger.success("Battery initialized.")
        self.logger.info("Fetching initial battery status information...")
        self.get_status()
        self.get_charge_level()
        self.get_temperature()
        self.get_voltage()
        self.get_current()
        self.get_io_voltage()
        self.get_io_current()
        self.get_io_pwm(1)
        self.logger.info("Fetching power management settings...")
        self.get_power_off()
        self.get_wakeup_on_charge()
        self.get_watch_dog()
        self.get_system_power_switch()
        self.logger.info("Fetching pijuice battery configuration...")
        self.get_charging_config()
        self.get_battery_profile_status()
        self.get_battery_profile()
        self.get_battery_temp_sense_config()

    def set_low_power_mode(self):
        self.pijuice.config.SetChargeCurrent(500)  # 500 mA
        self.pijuice.config.SetChargeVoltage(4100)  # 4.1 V cutoff
        print("⚡ Set to LOW power mode (500 mA, 4.1 V)")

    def set_high_power_mode(self):
        self.pijuice.config.SetChargeCurrent(
            2000
        )  # 2000 mA (max depends on battery/power supply)
        self.pijuice.config.SetChargeVoltage(4200)  # 4.2 V cutoff
        print("⚡ Set to HIGH power mode (2000 mA, 4.2 V)")

    def calculate_remaining_battery_time(self):
        # Hardcoded battery properties
        battery_voltage_nominal = 3.7  # V
        battery_capacity_mAh = 1820  # mAh

        voltage = self.pijuice.status.GetBatteryVoltage()["data"] / 1000  # mV → V
        current = self.pijuice.status.GetBatteryCurrent()["data"] / 1000  # mA → A
        charge_pct = self.pijuice.status.GetChargeLevel()["data"]  # 0–100%

        # Energy remaining in Wh
        energy_wh = (
            battery_capacity_mAh / 1000 * battery_voltage_nominal * (charge_pct / 100)
        )

        power_w = voltage * current

        if power_w > 0:
            time_remaining_h = energy_wh / power_w
            time_remaining_min = time_remaining_h * 60
        else:
            time_remaining_min = float("inf")  # charging or zero draw

        print(f"Estimated battery life remaining: {time_remaining_min:.1f} minutes")
        return time_remaining_min

    def get_energy_consumption(self):
        voltage = self.pijuice.status.GetBatteryVoltage()["data"] / 1000  # mV → V
        current = self.pijuice.status.GetBatteryCurrent()["data"] / 1000  # mA → A
        power = voltage * current
        print(f"Battery power: {power:.2f} W")
        return power

    def get_status(self):
        try:
            status = self.pijuice.status.GetStatus()
            self.logger.info(f"Current battery status: {status['data']}%")
            return status["data"]
        except Exception as e:
            self.logger.error(f"Failed to get battery charge level: {e}")
            return None

    def get_charge_level(self):
        try:
            charge_level = self.pijuice.status.GetChargeLevel()
            self.logger.info(f"Current battery charge level: {charge_level['data']}%")
            return charge_level["data"]
        except Exception as e:
            self.logger.error(f"Failed to get battery charge level: {e}")
            return None

    def get_temperature(self):
        try:
            battery_temperature = self.pijuice.status.GetBatteryTemperature()
            self.logger.info(f"Battery temperature: {battery_temperature['data']}°C")
            return battery_temperature["data"]
        except Exception as e:
            self.logger.error(f"Failed to get battery temperature: {e}")
            return None

    def get_voltage(self):
        # The returned value is Voltage in millivolts (mV).
        try:
            battery_voltage = self.pijuice.status.GetBatteryVoltage()
            self.logger.info(f"Battery voltage: {battery_voltage['data']} mV")
            return battery_voltage["data"]
        except Exception as e:
            self.logger.error(f"Failed to get battery voltage: {e}")
            return None

    def get_current(self):
        # The returned value is Current in milliamps (mA).
        try:
            battery_current = self.pijuice.status.GetBatteryCurrent()
            self.logger.info(f"Battery current: {battery_current['data']} mA")
            return battery_current["data"]
        except Exception as e:
            self.logger.error(f"Failed to get battery current: {e}")
            return None

    def get_io_voltage(self):
        # Value returned is voltage supplied from the GPIO power output from the PiJuice or when charging,
        # voltage value returned is supplied voltage. Value returned is in millivolts (mV).
        try:
            io_voltage = self.pijuice.status.GetIoVoltage()
            self.logger.info(f"IO voltage: {io_voltage['data']} mV")
            return io_voltage["data"]
        except Exception as e:
            self.logger.error(f"Failed to get IO voltage: {e}")
            return None

    def get_io_current(self):
        # Value returned is current supplied from the GPIO power output from the PiJuice or when charging,
        # current value returned is supplied current. Value returned is in milliamps (mA).
        try:
            io_current = self.pijuice.status.GetIoCurrent()
            self.logger.info(f"IO current: {io_current['data']} mA")
            return io_current["data"]
        except Exception as e:
            self.logger.error(f"Failed to get IO current: {e}")
            return None

    def get_io_pwm(self, pin):
        # Gets current PWM duty circle at IO pin configured as PWM output.
        try:
            io_pwm = self.pijuice.status.GetIoPWM(pin)
            self.logger.info(f"IO PWM for pin: {pin} is {io_pwm['data']}%")
            return io_pwm["data"]
        except Exception as e:
            self.logger.error(f"Failed to get IO PWM: {e}")
            return None

    def get_power_off(self):
        # Returns the power off state of the PiJuice.
        # 255 "Disabled" — i.e., the PiJuice is not currently set to power off at all.
        # Possible values:
        # 0 - Power off immediately after Pi shutdown
        # 1-254 - Power off after that many seconds (delay before cutting power)
        try:
            power_off = self.pijuice.power.GetPowerOff()
            self.logger.info(f"Power off state: {power_off['data']}")
            return power_off["data"]
        except Exception as e:
            self.logger.error(f"Failed to get power off state: {e}")
            return None

    def set_power_off(self, seconds):
        # Sets the power off state of the PiJuice.
        # seconds: 0 - Power off immediately after Pi shutdown,
        # 1-254 - Power off after that many seconds (delay before cutting power)
        try:
            self.pijuice.power.SetPowerOff(seconds)
            self.logger.success(f"Power off set to {seconds} seconds.")
        except Exception as e:
            self.logger.error(f"Failed to set power off state: {e}")

    def get_wakeup_on_charge(self):
        # Returns the wakeup on charge state of the PiJuice.
        try:
            wakeup_on_charge = self.pijuice.power.GetWakeUpOnCharge()
            self.logger.info(f"Wakeup on charge state: {wakeup_on_charge['data']}")
            return wakeup_on_charge["data"]
        except Exception as e:
            self.logger.error(f"Failed to get wakeup on charge state: {e}")
            return None

    def set_wakeup_on_charge(self, percentage):
        # Sets the wakeup on charge state of the PiJuice.
        try:
            self.pijuice.power.SetWakeUpOnCharge(percentage)
            self.logger.success(f"Wakeup on charge set to {percentage}%.")
        except Exception as e:
            self.logger.error(f"Failed to set wakeup on charge state: {e}")

    def get_watch_dog(self):
        # Returns the watchdog state of the PiJuice.
        # 0 means it is diabled
        try:
            watch_dog = self.pijuice.power.GetWatchdog()
            self.logger.info(f"Watchdog state: {watch_dog['data']}")
            return watch_dog["data"]
        except Exception as e:
            self.logger.error(f"Failed to get watchdog state: {e}")
            return None

    def set_watch_dog(self, minutes):
        # Sets the watchdog state of the PiJuice.
        try:
            self.pijuice.power.SetWatchdog(minutes)
            self.logger.success(f"Watchdog set to {minutes} minutes.")
        except Exception as e:
            self.logger.error(f"Failed to set watchdog state: {e}")

    def get_system_power_switch(self):
        # Returns the system power switch state of the PiJuice.
        try:
            system_power_switch = self.pijuice.power.GetSystemPowerSwitch()
            self.logger.info(
                f"System power switch state: {system_power_switch['data']}"
            )
            return system_power_switch["data"]
        except Exception as e:
            self.logger.error(f"Failed to get system power switch state: {e}")
            return None

    def set_system_power_switch(self, state):
        # Sets the system power switch state of the PiJuice.
        # State allowed values:
        # 0 - turn the power off
        # 500 - allows 500mA current (low power mode)
        # 2100 - allows 2100mA current (high power mode)
        try:
            self.pijuice.power.SetSystemPowerSwitch(state)
            self.logger.success(f"System power switch set to {state}.")
        except Exception as e:
            self.logger.error(f"Failed to set system power switch state: {e}")

    def get_charging_config(self):
        # Returns the charging configuration of the PiJuice.
        try:
            charging_config = self.pijuice.config.GetChargingConfig()
            self.logger.info(f"Charging configuration: {charging_config}")
            return charging_config
        except Exception as e:
            self.logger.error(f"Failed to get charging configuration: {e}")
            return None

    def set_charging_config(self, config):
        # Sets the charging configuration of the PiJuice.
        # {'charging_enabled':True} Charing enabled value can be True (Enabled) or False (Disabled).
        try:
            self.pijuice.config.SetChargingConfig(config)
            self.logger.success("Charging configuration set successfully.")
        except Exception as e:
            self.logger.error(f"Failed to set charging configuration: {e}")

    def set_battery_profile(self, profile):
        # Sets the battery profile of the PiJuice.
        # Available profiles: 'BP6X_1400', 'BP7X_1820', 'SNN5843_2300', 'PJLIPO_12000', 'PJLIPO_5000',
        # 'PJBP7X_1600', 'PJSNN5843_1300', 'PJZERO_1200', 'PJZERO_1000', 'PJLIPO_600', 'PJLIPO_500',
        # DEFAULT - means profile will be configured based on the DIP switch set on the PiJuice HAT.
        try:
            self.pijuice.config.SetBatteryProfile(profile)
            self.logger.success(f"Battery profile set to {profile}.")
        except Exception as e:
            self.logger.error(f"Failed to set battery profile: {e}")

    def get_battery_profile_status(self):
        # Returns the current battery profile status of the PiJuice.
        try:
            battery_profile_status = self.pijuice.config.GetBatteryProfileStatus()
            self.logger.info(
                f"Battery profile status: {battery_profile_status['data']}"
            )
            return battery_profile_status["data"]
        except Exception as e:
            self.logger.error(f"Failed to get battery profile status: {e}")
            return None

    def get_battery_profile(self):
        # Returns the current battery profile of the PiJuice.
        try:
            battery_profile = self.pijuice.config.GetBatteryProfile()
            self.logger.info(f"Current battery profile: {battery_profile['data']}")
            return battery_profile["data"]
        except Exception as e:
            self.logger.error(f"Failed to get battery profile: {e}")
            return None

    def get_battery_temp_sense_config(self):
        # Returns the battery temperature sense configuration of the PiJuice.
        # NOT_USED - No temperature sensor will be used
        # NTC - Use batteries built-in NTC as per battery NTC terminal
        # ON_BOARD - Use temperature sensor on MCU
        # AUTO_DETECT - Let the PiJuice software determine which method to use
        try:
            temp_sense_config = self.pijuice.config.GetBatteryTempSenseConfig()
            self.logger.info(
                f"Battery temperature sense configuration: {temp_sense_config['data']}"
            )
            return temp_sense_config["data"]
        except Exception as e:
            self.logger.error(
                f"Failed to get battery temperature sense configuration: {e}"
            )
            return None

    def set_battery_temp_sense_config(self, config):
        # Sets the battery temperature sense configuration of the PiJuice.
        # Returns the battery temperature sense configuration of the PiJuice.
        # NOT_USED - No temperature sensor will be used
        # NTC - Use batteries built-in NTC as per battery NTC terminal
        # ON_BOARD - Use temperature sensor on MCU
        # AUTO_DETECT - Let the PiJuice software determine which method to use
        try:
            self.pijuice.config.SetBatteryTempSenseConfig(config)
            self.logger.success(
                "Battery temperature sense configuration set successfully."
            )
        except Exception as e:
            self.logger.error(
                f"Failed to set battery temperature sense configuration: {e}"
            )
