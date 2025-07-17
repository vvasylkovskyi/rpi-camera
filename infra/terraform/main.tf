resource "aws_iot_thing" "thing" {
  name = "raspberry-pi-camera"
}

resource "aws_iot_policy" "publish_policy" {
  name = "RaspberryPiPublishPolicy"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "iot:Connect",
          "iot:Publish"
        ],
        "Resource": "*"
      }
    ]
  })
}

resource "aws_iot_certificate" "device_cert" {
  active = true
}
resource "aws_iot_thing_principal_attachment" "attach_cert" {
  thing       = aws_iot_thing.thing.id
  principal   = aws_iot_certificate.device_cert.arn
}

resource "aws_iot_policy_attachment" "attach_policy" {
  policy     = aws_iot_policy.publish_policy.name
  target     = aws_iot_certificate.device_cert.arn
}