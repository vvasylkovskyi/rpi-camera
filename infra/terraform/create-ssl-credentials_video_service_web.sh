#!/bin/bash

set -euo pipefail

OUTPUT_DIR="../aws_iot_ssl_credentials_video_service_web"

mkdir -p "$OUTPUT_DIR"

echo "Saving device.pem.crt..."
terraform output -raw iot_thing_video_service_web_certificate_pem > "$OUTPUT_DIR/device.pem.crt"

echo "Saving private.pem.key..."
terraform output -raw iot_thing_video_service_web_private_key > "$OUTPUT_DIR/private.pem.key"

echo "Downloading AmazonRootCA1.pem..."
curl -sS https://www.amazontrust.com/repository/AmazonRootCA1.pem -o "$OUTPUT_DIR/AmazonRootCA1.pem"

echo "Setting correct permissions..."
chmod 600 "$OUTPUT_DIR/private.pem.key"
chmod 644 "$OUTPUT_DIR/"*.pem*

echo "✅ Certificate files saved in $OUTPUT_DIR"