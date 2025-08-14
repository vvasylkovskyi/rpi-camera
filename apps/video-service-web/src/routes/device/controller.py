
from http.client import HTTPException
from fastapi import APIRouter, Depends, Request, status
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.http.response import handle_response
from shared.logger.logger import Logger
from shared.models.api_response import APIResponse
from shared.models.device_control_event import (
    DeviceControlAction,
    DeviceControlRequestEvent,
    DeviceControlResponseEvent,
)
from shared.mqtt.mqtt_clients import MQTTClients
from shared.mqtt.mqtt_topics import MQTTTopics
from sqlmodel import Session

from auth.dependencies import get_current_user
from database.models.device import Device
from database.session import get_session
from database.managers.device_manager import DeviceManager
from mqtt_rpc_client.mqtt_rpc_client import MqttRpcClient

device_router = APIRouter(prefix="/device")
logger = Logger("device_router")



@device_router.post("/", response_model=Device)
def create_device(device: Device, session: Session = Depends(get_session)):
    device_manager = DeviceManager(session)
    return device_manager.create_device(device)

@device_router.get("/", response_model=list[Device])
def list_devices(session: Session = Depends(get_session)):
    device_manager = DeviceManager(session)
    return device_manager.get_devices()

@device_router.get("/{device_id}", response_model=Device)
def read_device(device_id: int, session: Session = Depends(get_session)):
    device_manager = DeviceManager(session)
    device = device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@device_router.put("/{device_id}", response_model=Device)
def update_device(device_id: int, device: Device, session: Session = Depends(get_session)):
    device_manager = DeviceManager(session)
    updated = device_manager.update_device(device_id, device.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated

@device_router.delete("/{device_id}")
def delete_device(device_id: int, session: Session = Depends(get_session)):
    device_manager = DeviceManager(session)
    deleted = device_manager.delete_device(device_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"ok": True}


@device_router.post("/operation/shutdown", response_model=APIResponse)
def shutdown(_: Request, user_id: str = Depends(get_current_user)):    
    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)
    
    event = DeviceControlRequestEvent(
        action=DeviceControlAction.SHUTDOWN.value,
    )

    mqtt_client.publish(MQTTTopics.DEVICE_CONTROL.value, event.json())
    return handle_response(data={"OK": "OK"}, status_code=status.HTTP_200_OK)


@device_router.get("/operation/restart", response_model=APIResponse)
def restart(_: Request, user_id: str = Depends(get_current_user)):    
    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    event = DeviceControlRequestEvent(
        action=DeviceControlAction.RESTART.value,
    )

    mqtt_client.publish(MQTTTopics.DEVICE_CONTROL.value, event.json())
    return handle_response(data={"OK": "OK"}, status_code=status.HTTP_200_OK)


@device_router.get("/operation/health-check", response_model=APIResponse)
async def get_health_check(_: Request, user_id: str = Depends(get_current_user)):
    mqtt_rpc_client = MqttRpcClient()
    device_id = "rpi-camera-device"
    event = DeviceControlRequestEvent(
        action=DeviceControlAction.GET_HEALTH_CHECK.value,
    )

    try:
        result: dict = await mqtt_rpc_client.call(MQTTTopics.DEVICE_CONTROL.with_device(device_id), event.json())
        DeviceControlResponseEvent.validate(result)
        return handle_response(data=result, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return handle_response(
            error="Health check failed: " + str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

