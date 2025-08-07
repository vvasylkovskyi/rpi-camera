from enum import Enum


class MQTTClients(Enum):
    DEVICE = "device/{device_id}"
    WEB_SERVICE = "video-service-web/{device_id}"

    def with_device(self, device_id: str) -> str:
        return self.value.format(device_id=device_id)
