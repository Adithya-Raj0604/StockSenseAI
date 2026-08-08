# Raw EC2 app instance in a PRIVATE subnet. No public IP: SSH only via the
# bastion, egress only via the NAT gateway. This is the "real EC2 in a VPC"
# proof — the always-on public link is Lightsail, this is the genuine article.

resource "aws_security_group" "app" {
  name        = "${var.name}-app-sg"
  description = "App instance: SSH from bastion, app port from within VPC, all egress."
  vpc_id      = var.vpc_id

  ingress {
    description     = "SSH from bastion only"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [var.bastion_security_group_id]
  }

  ingress {
    description = "App port from within the VPC (e.g. a load balancer / bastion curl)"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]
  }

  egress {
    description = "All egress (pulls image / packages via NAT)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.name}-app-sg" })
}

# Minimal user-data: install Docker and run the server-mode image.
# The image is expected in ECR (built from backend/Dockerfile.server).
locals {
  user_data = <<-EOT
    #!/bin/bash
    set -euo pipefail
    dnf install -y docker || yum install -y docker
    systemctl enable --now docker
    aws ecr get-login-password --region ${var.region} \
      | docker login --username AWS --password-stdin ${var.ecr_registry}
    docker run -d --restart unless-stopped \
      -p ${var.app_port}:8000 \
      -e DEPLOYMENT=self-hosted \
      ${var.container_image}
  EOT
}

resource "aws_instance" "app" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = var.iam_instance_profile
  user_data              = local.user_data

  tags = merge(var.tags, { Name = "${var.name}-app" })
}
