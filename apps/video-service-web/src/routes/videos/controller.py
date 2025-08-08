from fastapi import APIRouter, Request, Depends, status

from shared.http.response import handle_response
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
from auth.dependencies import get_current_user

videos_router = APIRouter(prefix="/video")
logger = Logger("videos_router")


@videos_router.get("/")
async def get_all_videos(user_id: str = Depends(get_current_user)):
    logger.info("Received request to get all videos")
    return handle_response(data={"status": "All videos retrieved successfully", "user_id": user_id}, status_code=status.HTTP_200_OK)


@videos_router.post("/start-webrtc")
async def start_streaming_service(request: Request, user_id: str = Depends(get_current_user)):
    device_id = "rpi-camera-device"
    body = await request.json()
    offer_type = body.get("type")
    offer_sdp = body.get("sdp")

    event = CameraControlEvent(
        action=CameraAction.START_WEBRTC_STREAM,
        webrtc_offer=WebRTCOffer(type=offer_type, sdp=offer_sdp),
    )

    mqtt_rpc_client = MqttRpcClient()

    result: dict = await mqtt_rpc_client.call(MQTTTopics.CAMERA_CONTROL.with_device(device_id), event.json(), 180)
    
    return handle_response(data={
        "status": "success",
        "webrtc_answer": result["webrtc_answer"],
    }, status_code=status.HTTP_200_OK)


@videos_router.get("/stop-webrtc")
async def stop_webrtc(user_id: str = Depends(get_current_user)):
    device_id = "rpi-camera-device"
    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    event = CameraControlEvent(
        action=CameraAction.STOP_WEBRTC_STREAM,
    )

    mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.with_device(device_id), event.json())

    return handle_response(data={
        "status": "Video streaming service stopped successfully",
    }, status_code=status.HTTP_200_OK)
