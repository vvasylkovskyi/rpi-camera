
module "network" {
  source            = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/network?ref=main"
  vpc_cidr          = "10.0.0.0/16"
  subnet_cidr       = "10.0.1.0/24"
  availability_zone = var.availability_zone
}

module "security_group" {
  source = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/security_group?ref=main"
  vpc_id = module.network.vpc_id
}

module "ec2" {
  source              = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/ec2?ref=main"
  instance_ami        = var.instance_ami
  instance_type       = var.instance_type
  availability_zone   = var.availability_zone
  security_group_id   = module.security_group.security_group_ec2
  subnet_id           = module.network.public_subnet_ids[0]
  ssh_public_key      = file("~/.ssh/${var.ssh_public_key_name}.pub")
  ssh_public_key_name = var.ssh_public_key_name

  user_data = <<-EOF
            #!/bin/bash
            # Update packages
            sudo apt-get update -y

            sudo apt-get install -y nginx

            # Start and enable nginx service
            sudo systemctl start nginx
            sudo systemctl enable nginx

            # Configure reverse proxy
            sudo tee /etc/nginx/conf.d/reverse_proxy.conf > /dev/null <<EOL
            server {
                listen 80;
                server_name ${var.domain_name};

                location / {
                    proxy_pass http://localhost:${var.container_port};
                    proxy_set_header Host \$host;
                    proxy_set_header X-Real-IP \$remote_addr;
                    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto \$scheme;
                }
            }
            EOL

            # Reload nginx to apply config
            sudo systemctl reload nginx

            EOF
}

module "aws_route53_record" {
  source          = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/dns?ref=main"
  domain_name     = var.domain_name
  route53_zone_id = var.route53_zone_id
  dns_record      = module.ec2.public_ip
  aws_lb_dns_name = module.alb.aws_lb_dns_name
  aws_lb_zone_id  = module.alb.aws_lb_zone_id
}

module "ssl_acm" {
  source              = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/acm?ref=main"
  domain_name         = var.domain_name
  aws_route53_zone_id = module.aws_route53_record.aws_route53_zone_id
}

module "alb" {
  source                   = "git::https://github.com/vvasylkovskyi/vvasylkovskyi-infra.git//modules/alb?ref=main"
  acm_certificate_arn      = module.ssl_acm.aws_acm_certificate_arn
  aws_acm_certificate_cert = module.ssl_acm.aws_acm_certificate_cert
  subnets                  = module.network.public_subnet_ids
  vpc_id                   = module.network.vpc_id
  security_group           = module.security_group.security_group_alb
  ec2_instance_id          = module.ec2.instance_id
  alb_name                 = var.alb_name
}
