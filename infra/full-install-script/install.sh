# #!/bin/bash
# set -euo pipefail

# API_URL="http://localhost:4000/api/v1/device/register"

# echo "Requesting certificates from API..."

# response=$(curl -s -X GET "$API_URL" \
#     -H "Content-Type: application/json")

HOME_PATH="$HOME"
# # Parse JSON using jq
DEVICE_ID=$(echo "$response" | jq -r '.data.deviceId')
CERTS_DIR="$HOME/aws_iot_ssl_credentials_$DEVICE_ID"
mkdir -p "$CERTS_DIR"

# Decode Base64 JSON to temporary file
echo "$response" | jq -r '.data.credsBase64' | base64 --decode > /tmp/creds.json

# Extract PEMs/keys
jq -r '.certificatePem' /tmp/creds.json > "$CERTS_DIR/device.pem.crt"
jq -r '.privateKey' /tmp/creds.json > "$CERTS_DIR/private.pem.key"
jq -r '.publicKey' /tmp/creds.json > "$CERTS_DIR/public.pem.key"
jq -r '.rootCA' /tmp/creds.json > "$CERTS_DIR/AmazonRootCA1.pem"

chmod 600 "$CERTS_DIR/private.pem.key"
chmod 644 "$CERTS_DIR/"*.pem*

AWS_IOT_CORE_ENDPOINT=$(echo "$response" | jq -r '.data.endpoint')
# echo "Certificates stored in $CERTS_DIR"

if ! command -v ansible-pull &>/dev/null; then
    sudo apt update
    sudo apt install -y ansible git
fi

ansible-pull -U https://github.com/vvasylkovskyi/rpi-camera.git -i localhost infra/ansible-configurations/playbooks/install-all.yml \
--extra-vars "certs_dir=$CERTS_DIR home_path=$HOME_PATH aws_iot_core_endpoint=$AWS_IOT_CORE_ENDPOINT device_id=$DEVICE_ID"
