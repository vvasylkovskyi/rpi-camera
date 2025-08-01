from fastapi import APIRouter, Request

from shared.logger.logger import Logger
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.models.camera_control_event import (
    CameraControlEvent,
    CameraAction,
    WebRTCOffer,
)
from shared.mqtt.mqtt_topics import MQTTTopics
from shared.mqtt.mqtt_clients import MQTTClients
from mqtt_rpc_client.mqtt_rpc_client import MqttRpcClient

videos_router = APIRouter(prefix="/video")
logger = Logger("videos_router")


@videos_router.get("/")
async def get_all_videos():
    logger.info("Received request to get all videos")
    return {"status": "All videos retrieved successfully"}


@videos_router.post("/start-webrtc")
async def start_streaming_service(request: Request):    
    body = await request.json()
    offer_type = body.get("type")
    offer_sdp = body.get("sdp")

    event = CameraControlEvent(
        action=CameraAction.START_WEBRTC_STREAM,
        webrtc_offer=WebRTCOffer(type=offer_type, sdp=offer_sdp),
    )

    mqtt_rpc_client = MqttRpcClient()

    result: dict = await mqtt_rpc_client.call(MQTTTopics.CAMERA_CONTROL.value, event.json(), 180)
    return {
        "status": "success",
        "webrtc_answer": result["webrtc_answer"],
    }


@videos_router.get("/stop-webrtc")
async def stop_webrtc():

    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    event = CameraControlEvent(
        action=CameraAction.STOP_WEBRTC_STREAM,
    )

    mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())

    return {
        "status": "Video streaming service stopped successfully",
    }
