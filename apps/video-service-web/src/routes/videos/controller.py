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
from shared.mqtt.mqtt_topics import MQTTTopics
from shared.mqtt.mqtt_clients import MQTTClients

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

    mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    event = CameraControlEvent(
        action=CameraAction.START_WEBRTC_STREAM,
        webrtc_offer=WebRTCOffer(type=offer_type, sdp=offer_sdp),
    )

    mqtt_client.publish(MQTTTopics.CAMERA_CONTROL.value, event.json())

    # Future to be set when a matching MQTT message arrives
    message_future = asyncio.get_event_loop().create_future()

    # Wait for 20 seconds to ensure the stream is available
    # success = await ffmpeg_service.start_and_wait(20)
    # Callback for MQTT subscription
    def on_message_received(topic, payload, **kwargs):
        try:
            logger.info(f"Received MQTT message on topic {topic}, payload: {payload}")
            data: CameraControlEvent = json.loads(payload.decode())
            if (
                not message_future.done()
                and data["action"] == CameraAction.START_WEBRTC_STREAM_ANSWER.value
            ):
                message_future.set_result(data)
        except Exception as e:
            logger.error(f"MQTT message parse error: {e}")

    await mqtt_client.subscribe(
        MQTTTopics.CAMERA_WEBCAM_STREAM.value, on_message_received
    )

    try:
        response: CameraControlEvent = await asyncio.wait_for(
            message_future, timeout=10
        )
        logger.info(
            f"Received response from camera, sending to client: {response['webrtc_answer']}"
        )
        return {
            "status": "success",
            "webrtc_answer": response["webrtc_answer"],
        }
    except asyncio.TimeoutError:
        return {
            "status": "error",
            "message": "Timed out waiting for camera response",
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
