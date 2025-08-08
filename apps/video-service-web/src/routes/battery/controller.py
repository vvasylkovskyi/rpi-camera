
from fastapi import APIRouter, Request, Depends, status
from shared.http.response import handle_response
from shared.logger.logger import Logger
from shared.models.battery_info_event import BatteryAction, BatteryInfoRequestEvent, BatteryInfoResponseEvent
from shared.mqtt.mqtt_topics import MQTTTopics

from mqtt_rpc_client.mqtt_rpc_client import MqttRpcClient
from auth.dependencies import get_current_user

battery_router = APIRouter(prefix="/battery")
logger = Logger("battery_router")

@battery_router.get("/health-check")
async def health_check(_: Request, user_id: str = Depends(get_current_user)):    
    device_id = "rpi-camera-device"
    mqtt_rpc_client = MqttRpcClient()
    event = BatteryInfoRequestEvent(
        action=BatteryAction.GET_HEALTH_CHECK.value,
    )

    try:
        result: dict = await mqtt_rpc_client.call(MQTTTopics.BATTERY_CONTROL.with_device(device_id), event.json())
        BatteryInfoResponseEvent.validate(result)
        return handle_response(data=result, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return handle_response(
            error="Health check failed: " + str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

