output "iot_thing_raspberry_pi_4b_certificate_pem" {
  value     = module.iot_thing_raspberry_pi_4b.certificate_pem
  sensitive = true
}

output "iot_thing_raspberry_pi_4b_private_key" {
  value     = module.iot_thing_raspberry_pi_4b.private_key
  sensitive = true
}

output "iot_thing_raspberry_pi_4b_public_key" {
  value     = module.iot_thing_raspberry_pi_4b.public_key
  sensitive = true
}

output "iot_thing_raspberry_pi_4b_certificate_arn" {
  value = module.iot_thing_raspberry_pi_4b.certificate_arn
}

output "iot_thing_video_service_web_certificate_pem" {
  value     = module.iot_thing_video_service.certificate_pem
  sensitive = true
}

output "iot_thing_video_service_web_private_key" {
  value     = module.iot_thing_video_service.private_key
  sensitive = true
}

output "iot_thing_video_service_web_public_key" {
  value     = module.iot_thing_video_service.public_key
  sensitive = true
}

output "iot_thing_video_service_web_certificate_arn" {
  value = module.iot_thing_video_service.certificate_arn
}

output "iot_endpoint" {
  value = module.iot_thing_raspberry_pi_4b.iot_endpoint
}