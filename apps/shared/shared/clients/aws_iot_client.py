import json
import os
import base64
import boto3

from shared.logger.logger import Logger


class AwsIoTClient:
    def __init__(self):
        self.logger = Logger("AwsIoTClient")
        self.iot = boto3.client("iot")

    def provision_device_credentials(self, device_id: str) -> str | None:
        # 1. Create IoT Thing
        self.iot.create_thing(thingName=device_id)

        # 2. Create Policy (idempotent - check if exists)
        policy_name = f"{device_id}-policy"
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iot:Connect",
                        "iot:Publish",
                        "iot:Subscribe",
                        "iot:Receive",
                    ],
                    "Resource": "*",
                }
            ],
        }

        try:
            self.iot.create_policy(
                policyName=policy_name, policyDocument=json.dumps(policy_document)
            )
        except self.iot.exceptions.ResourceAlreadyExistsException:
            print(f"Policy {policy_name} already exists, reusing it.")

        # 3. Create certificate + keys
        cert = self.iot.create_keys_and_certificate(setAsActive=True)

        # 4. Attach policy to certificate
        self.iot.attach_policy(policyName=policy_name, target=cert["certificateArn"])

        # 5. Attach certificate to Thing
        self.iot.attach_thing_principal(
            thingName=device_id, principal=cert["certificateArn"]
        )

        # 6. Get IoT endpoint (data ATS)
        endpoint = self.iot.describe_endpoint(endpointType="iot:Data-ATS")[
            "endpointAddress"
        ]

        return {
            "deviceId": device_id,
            "certificatePem": base64.b64encode(
                cert["certificatePem"].encode("utf-8")
            ).decode("utf-8"),
            "privateKey": base64.b64encode(
                cert["keyPair"]["PrivateKey"].encode("utf-8")
            ).decode("utf-8"),
            "publicKey": base64.b64encode(
                cert["keyPair"]["PublicKey"].encode("utf-8")
            ).decode("utf-8"),
            "certificateArn": cert["certificateArn"],
            "endpoint": endpoint,
            "policyName": policy_name,
        }
