import json
import uuid
import asyncio
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.mqtt.mqtt_clients import MQTTClients

class MqttRpcClient:
    def __init__(self):
        self.mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    async def call(self, request_topic: str, payload: str, timeout: int = 10) -> dict:
            request_id = str(uuid.uuid4())
            reply_topic = f"{request_topic}/response/{request_id}"
            
            payload_dict = json.loads(payload)
            payload_dict["request_id"] = request_id
            encoded_payload = json.dumps(payload_dict)
            
            # Future that will be set once response arrives
            future = asyncio.get_event_loop().create_future()

            # Callback to handle incoming response message
            def on_response(topic, payload, **kwargs):
                try:
                    data = json.loads(payload.decode())
                    if not future.done():
                        future.set_result(data)
                except Exception as e:
                    if not future.done():
                        future.set_exception(e)

            try:
                # Subscribe to the reply topic
                await self.mqtt_client.subscribe(reply_topic, on_response)

                # Publish the request
                self.mqtt_client.publish(request_topic, encoded_payload)

                # Wait for response or timeout
                return await asyncio.wait_for(future, timeout=timeout)

            except asyncio.TimeoutError:
                raise TimeoutError(f"MQTT call timed out after {timeout}s for topic '{request_topic}'")

            finally:
                # Always unsubscribe to avoid leaks
                await self.mqtt_client.unsubscribe(reply_topic)
  