
from fastapi import APIRouter, Request, Depends, status
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

from mqtt_rpc_client.mqtt_rpc_client import MqttRpcClient
from auth.dependencies import get_current_user

device_router = APIRouter(prefix="/device")
logger = Logger("device_router")

@device_router.post("/shutdown", response_model=APIResponse)
def shutdown(_: Request, user_id: str = Depends(get_current_user)):    
    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)
    
    event = DeviceControlRequestEvent(
        action=DeviceControlAction.SHUTDOWN.value,
    )

    mqtt_client.publish(MQTTTopics.DEVICE_CONTROL.value, event.json())
    return handle_response(data={"OK": "OK"}, status_code=status.HTTP_200_OK)


@device_router.get("/restart", response_model=APIResponse)
def restart(_: Request, user_id: str = Depends(get_current_user)):    
    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    event = DeviceControlRequestEvent(
        action=DeviceControlAction.RESTART.value,
    )

    mqtt_client.publish(MQTTTopics.DEVICE_CONTROL.value, event.json())
    return handle_response(data={"OK": "OK"}, status_code=status.HTTP_200_OK)


@device_router.get("/health-check", response_model=APIResponse)
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

