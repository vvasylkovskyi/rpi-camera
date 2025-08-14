from typing import Optional
from sqlmodel import Session, select
from database.models.device import Device

class DeviceManager:
    def __init__(self, session: Session):
        self.database_session = session

    def create_device(self, device: Device) -> Device:
        self.database_session.add(device)
        self.database_session.commit()
        self.database_session.refresh(device)
        return device

    def get_device(self, device_id: int) -> Optional[Device]:
        return self.database_session.get(Device, device_id)

    def get_devices(self) -> list[Device]:
        return self.database_session.exec(select(Device)).all()

    def update_device(self, device_id: int, new_data: dict) -> Optional[Device]:
        device = self.database_session.get(Device, device_id)
        if not device:
            return None
        for key, value in new_data.items():
            setattr(device, key, value)
        self.database_session.add(device)
        self.database_session.commit()
        self.database_session.refresh(device)
        return device

    def delete_device(self, device_id: int) -> bool:
        device = self.database_session.get(Device, device_id)
        if not device:
            return False
        self.database_session.delete(device)
        self.database_session.commit()
        return True
