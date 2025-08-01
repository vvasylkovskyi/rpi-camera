import json
# import uuid
import asyncio
from shared.clients.aws_mqtt_client import AwsMQTTClient
from shared.mqtt.mqtt_clients import MQTTClients

class MqttRpcClient:
    def __init__(self):
        self.mqtt_client = AwsMQTTClient(MQTTClients.WEB_SERVICE.value)

    async def call(self, request_topic: str, payload: str, timeout: int = 10) -> dict:
            # request_id = str(uuid.uuid4())
            reply_topic = f"{request_topic}/response"
            # Add correlation info into the payload
            # payload = payload.copy()
            # payload.update({
            #     "request_id": request_id,
            #     "reply_to": reply_to,
            # })

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

            # Subscribe to the reply topic
            await self.mqtt_client.subscribe(reply_topic, on_response)

            # Publish the request
            self.mqtt_client.publish(request_topic, payload)

            # Wait for response or timeout
            response = await asyncio.wait_for(future, timeout=timeout)

            return response
