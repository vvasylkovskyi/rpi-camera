#!/bin/bash

set -euo pipefail

# Read and encode each piece
CERT=$(terraform output -raw iot_thing_video_service_web_certificate_pem | base64 -w 0)
KEY=$(terraform output -raw iot_thing_video_service_web_private_key | base64 -w 0)
ROOT_CA=$(curl -sS https://www.amazontrust.com/repository/AmazonRootCA1.pem | base64 -w 0)

# Print as JSON
cat <<EOF
{
  "certificate_pem": "$CERT",
  "private_key": "$KEY",
  "amazon_root_ca": "$ROOT_CA"
}
EOF
