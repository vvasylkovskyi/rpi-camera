import asyncio
import os
from rpi_camera.clients.aws_mqtt_client import AwsMQTTClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rpi_camera.routes.routes import create_router
from rpi_camera.logger.logger import Logger 

logger = Logger("main")

app = FastAPI(title="RPI Camera API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(create_router())

# Initialize the MQTT client
mqtt_client = AwsMQTTClient()

# Keep a reference to the background task
mqtt_task: asyncio.Task | None = None


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    try:
        await mqtt_client.connect()
        logger.success("MQTT client connected successfully.")
    except Exception as e:
        logger.error(f"MQTT client connection failed: {e}")

    # # Launch the MQTT message handler loop as a background task
    # global mqtt_task
    # mqtt_task = asyncio.create_task(mqtt_client.handle_messages())
    # logger.info("MQTT message handler task started.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
    if mqtt_task:
        logger.info("Cancelling MQTT message handler task...")
        mqtt_task.cancel()
        try:
            await mqtt_task
        except asyncio.CancelledError:
            logger.info("MQTT message handler task cancelled successfully.")
    try:
        await mqtt_client.disconnect()
        logger.success("MQTT client disconnected successfully.")
    except Exception as e:
        logger.error(f"MQTT client disconnect failed: {e}")
