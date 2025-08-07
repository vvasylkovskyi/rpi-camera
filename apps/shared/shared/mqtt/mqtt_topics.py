from enum import Enum

class MQTTTopics(Enum):
    CAMERA_CONTROL = "looney/{device_id}/camera/control/set"
    BATTERY_CONTROL = "looney/{device_id}/battery/control/set"
    DEVICE_CONTROL = "looney/{device_id}/device/control/set"

    def with_device(self, device_id: str) -> str:
        return self.value.format(device_id=device_id)
