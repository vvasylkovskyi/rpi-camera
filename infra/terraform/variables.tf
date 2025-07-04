variable "availability_zone" {
  description = "Availability zone of resources"
  type        = string
}

variable "instance_ami" {
  description = "ID of the AMI used"
  type        = string
}

variable "instance_type" {
  description = "Type of the instance"
  type        = string
}

variable "domain_name" {
  description = "domain name"
  type        = string
}

variable "route53_zone_id" {
  description = "Route 53 Zone Id"
  type        = string
}

variable "lock_table" { type = string }
variable "aws_region" { type = string }
variable "backend_bucket" { type = string }
variable "container_port" { type = string }
variable "ssh_public_key_name" { type = string }
variable "alb_name" { type = string }
