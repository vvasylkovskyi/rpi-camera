from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from video_service_web.routes.routes import create_router
from video_service_web.logger.logger import Logger
from video_service_web.clients.aws_mqtt_client import AwsMQTTClient

logger = Logger("main")

app = FastAPI(title="Video Service Web API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(create_router())

# Initialize the MQTT client
mqtt_client = AwsMQTTClient()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    try:
        await mqtt_client.connect()
        await mqtt_client.subscribe()
        logger.success("MQTT client connected successfully.")
    except Exception as e:
        logger.error(f"MQTT client connection failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
    try:
        await mqtt_client.disconnect()
        logger.success("MQTT client disconnected successfully.")
    except Exception as e:
        logger.error(f"MQTT client disconnect failed: {e}")
