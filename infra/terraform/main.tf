module "iot_thing_raspberry_pi_4b" {
  source = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/iot-thing"
  iot_thing_name  = "raspberry-pi-camera-4b"
  iot_policy_name = "raspberry-pi-camera-4b-policy"
  iot_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "iot:Connect",
          "iot:Publish",
          "iot:Subscribe",
          "iot:Receive"
        ],
        "Resource": "*"
      }
    ]
  })
}

module "iot_thing_video_service" {
  source = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/iot-thing"
  iot_thing_name  = "video-service-web"
  iot_policy_name = "video-service-web-policy"
  iot_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "iot:Connect",
          "iot:Publish",
          "iot:Subscribe",
          "iot:Receive"
        ],
        "Resource": "*"
      }
    ]
  })
}
