import os
import asyncio
import traceback
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from video_service_web.logger.logger import Logger
from video_service_web.utils.base64 import Base64
from video_service_web.mqtt_topics.mqtt_topics_manager import MqttTopicManager


class AwsMQTTClient:
    _instance = None
    logger = Logger("AwsMQTTClient")
    topic_manager = MqttTopicManager()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.ENDPOINT = os.environ["AWS_IOT_CORE_ENDPOINT"]
            cls._instance.CLIENT_ID = os.environ.get("AWS_IOT_CLIENT_ID")
            cls._instance.PATH_TO_CERT = os.environ["AWS_IOT_PATH_TO_CERT"]
            cls._instance.PATH_TO_KEY = os.environ["AWS_IOT_PATH_TO_KEY"]
            cls._instance.PATH_TO_ROOT = os.environ["AWS_IOT_PATH_TO_ROOT_CERT"]
            cls._instance.TOPIC = os.environ.get("AWS_IOT_MQTT_TOPIC")

            Base64.write_if_missing(cls._instance.PATH_TO_CERT, "AWS_IOT_CERT_BASE64")
            Base64.write_if_missing(cls._instance.PATH_TO_KEY, "AWS_IOT_KEY_BASE64")
            Base64.write_if_missing(
                cls._instance.PATH_TO_ROOT, "AWS_IOT_ROOT_CERT_BASE64"
            )

            cls._instance.event_loop_group = io.EventLoopGroup(1)
            cls._instance.host_resolver = io.DefaultHostResolver(
                cls._instance.event_loop_group
            )
            cls._instance.client_bootstrap = io.ClientBootstrap(
                cls._instance.event_loop_group, cls._instance.host_resolver
            )

            cls._instance.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=cls._instance.ENDPOINT,
                cert_filepath=cls._instance.PATH_TO_CERT,
                pri_key_filepath=cls._instance.PATH_TO_KEY,
                client_bootstrap=cls._instance.client_bootstrap,
                ca_filepath=cls._instance.PATH_TO_ROOT,
                client_id=cls._instance.CLIENT_ID,
                clean_session=False,
                keep_alive_secs=30,
            )

        return cls._instance

    def get_device_id(self):
        return self.CLIENT_ID

    async def connect(self):
        self.logger.info(
            f"Connecting to {self.ENDPOINT} with client ID '{self.CLIENT_ID}'..."
        )
        try:
            connect_future = self.mqtt_connection.connect()
            await asyncio.wrap_future(connect_future)
            self.logger.success("Connected!")
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            self.logger.debug(traceback.format_exc())
            raise

    async def publish(self, message: str):
        self.logger.info(f"Publishing message to topic '{self.TOPIC}': {message}")

        try:
            publish_future, packet_id = self.mqtt_connection.publish(
                topic=self.TOPIC, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE
            )

            # This will not block the event loop
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, publish_future.result)
            self.logger.success(
                f"Message published to topic '{self.TOPIC}' with packet ID {packet_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to publish message to topic '{self.TOPIC}': {e}")
            self.logger.debug(traceback.format_exc())
            return False

    async def subscribe(self):
        self.logger.info(f"Subscribing to topic '{self.TOPIC}'...")

        def on_message_received(topic, payload, **kwargs):
            self.topic_manager.handle_message(payload)

        try:
            subscribe_future, packet_id = self.mqtt_connection.subscribe(
                topic=self.TOPIC,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=on_message_received,
            )

            await asyncio.wrap_future(subscribe_future)
            self.logger.success(
                f"Successfully subscribed to topic '{self.TOPIC}' with packet ID {packet_id}"
            )
        except Exception as e:
            self.logger.error(f"Failed to subscribe to topic '{self.TOPIC}': {e}")
            self.logger.debug(traceback.format_exc())
            raise

    async def disconnect(self):
        self.logger.info("Disconnecting...")
        try:
            disconnect_future = self.mqtt_connection.disconnect()
            await asyncio.wrap_future(disconnect_future)
            self.logger.success("Disconnected.")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
            self.logger.debug(traceback.format_exc())
