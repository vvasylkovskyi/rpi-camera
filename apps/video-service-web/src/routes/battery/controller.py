
from fastapi import APIRouter, Request
from shared.logger.logger import Logger
from shared.models.battery_info_event import BatteryAction, BatteryInfoRequestEvent, BatteryInfoResponseEvent
from shared.mqtt.mqtt_topics import MQTTTopics

from mqtt_rpc_client.mqtt_rpc_client import MqttRpcClient

battery_router = APIRouter(prefix="/battery")
logger = Logger("battery_router")

@battery_router.get("/health-check")
async def health_check(_: Request):    
    mqtt_rpc_client = MqttRpcClient()
    event = BatteryInfoRequestEvent(
        action=BatteryAction.GET_HEALTH_CHECK.value,
    )

    result: dict = await mqtt_rpc_client.call(MQTTTopics.BATTERY_INFO.value, event.json())
    result = BatteryInfoResponseEvent.validate(result)
    return {
        "data": result
    }

