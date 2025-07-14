# rpi_camera/aws_s3_client.py

import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError

class S3Client:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3 = boto3.client("s3")

    def upload_file(self, filepath: str, object_key: str = None) -> str | None:
        if object_key is None:
            object_key = os.path.basename(filepath)

        try:
            self.s3.upload_file(filepath, self.bucket_name, object_key)
            s3_path = f"s3://{self.bucket_name}/{object_key}"
            print(f"✅ Uploaded to {s3_path}")
            return s3_path
        except (BotoCoreError, ClientError) as e:
            print(f"❌ S3 Upload failed: {e}")
            return None

    def generate_presigned_url(self, object_key: str, expires_in: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": object_key},
            ExpiresIn=expires_in,
        )
