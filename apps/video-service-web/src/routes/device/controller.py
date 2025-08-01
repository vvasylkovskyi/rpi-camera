from fastapi import APIRouter, Request
import asyncio
import json

from shared.logger.logger import Logger
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.models.camera_control_event import (
    CameraControlEvent,
    CameraAction,
    WebRTCOffer,
)
from shared.models.device_control_event import DeviceControlAction, DeviceControlRequestEvent
from shared.mqtt.mqtt_topics import MQTTTopics
from shared.mqtt.mqtt_clients import MQTTClients
from mqtt_rpc_client.mqtt_rpc_client import MqttRpcClient

device_router = APIRouter(prefix="/device")
logger = Logger("device_router")

@device_router.get("/health-check")
async def get_health_check(_: Request):    
    mqtt_rpc_client = MqttRpcClient()

    event = DeviceControlRequestEvent(
        action=DeviceControlAction.GET_HEALTH_CHECK,
    )

    result = await mqtt_rpc_client.call(MQTTTopics.DEVICE_CONTROL.value, MQTTTopics.DEVICE_CONTROL_RESPONSE.value, event.json())
    print(">>> Result: ", result)
    return {
        "status": "OK",
        "data": result.get("health_check_info", {})
    }

@device_router.get("/stop-webrtc")
async def stop_webrtc():

    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    event = CameraControlEvent(
        action=CameraAction.STOP_WEBRTC_STREAM,
    )

    mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())

    return {
        "status": "Video streaming service stopped successfully",
    }
