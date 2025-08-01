
from fastapi import APIRouter, Request
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.logger.logger import Logger
from shared.models.device_control_event import (
    DeviceControlAction,
    DeviceControlRequestEvent,
    DeviceControlResponseEvent,
)
from shared.mqtt.mqtt_topics import MQTTTopics

from mqtt_rpc_client.mqtt_rpc_client import MqttRpcClient

device_router = APIRouter(prefix="/device")
logger = Logger("device_router")

@device_router.post("/shutdown")
async def shutdown(_: Request):    
    mqtt_client = AwsMQTTClient()

    event = DeviceControlRequestEvent(
        action=DeviceControlAction.SHUTDOWN.value,
    )

    await mqtt_client.publish(MQTTTopics.DEVICE_CONTROL.value, event.json())
    
    return {
        "status": "OK",
    }

@device_router.get("/restart")
async def restart(_: Request):    
    mqtt_client = AwsMQTTClient()

    event = DeviceControlRequestEvent(
        action=DeviceControlAction.RESTART.value,
    )

    await mqtt_client.publish(MQTTTopics.DEVICE_CONTROL.value, event.json())
    return {
        "status": "OK",
    }

@device_router.get("/health-check")
async def get_health_check(_: Request):    
    mqtt_rpc_client = MqttRpcClient()

    event = DeviceControlRequestEvent(
        action=DeviceControlAction.GET_HEALTH_CHECK.value,
    )

    result: dict = await mqtt_rpc_client.call(MQTTTopics.DEVICE_CONTROL.value, MQTTTopics.DEVICE_CONTROL_RESPONSE.value, event.json())
    result = DeviceControlResponseEvent.validate(result)
    return {
        "status": "OK",
        "data": result
    }

