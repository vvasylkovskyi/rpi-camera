output "certificate_pem" {
  value     = aws_iot_certificate.device_cert.certificate_pem
  sensitive = true
}

output "private_key" {
  value     = aws_iot_certificate.device_cert.private_key
  sensitive = true
}

output "public_key" {
  value     = aws_iot_certificate.device_cert.public_key
  sensitive = true
}

output "certificate_arn" {
  value = aws_iot_certificate.device_cert.arn
}

output "iot_endpoint" {
  value = data.aws_iot_endpoint.iot_endpoint.endpoint_address
}