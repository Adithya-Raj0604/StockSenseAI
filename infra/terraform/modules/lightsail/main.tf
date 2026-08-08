# Always-on live host on Lightsail. Chosen over raw EC2 for the persistent
# demo because the bundle includes a static IP + data transfer (no separate
# ~$3.60/mo public-IPv4 charge) at a flat ~$5/mo. The raw-EC2/VPC path is still
# proven in the ephemeral full-demo environment; see infra/docs/production-ec2.md.

resource "aws_lightsail_instance" "this" {
  name              = var.name
  availability_zone = var.availability_zone
  blueprint_id      = var.blueprint_id # e.g. amazon_linux_2023
  bundle_id         = var.bundle_id    # e.g. small_3_0 (1 GB) — 512 MB likely OOMs the model

  # Installs Docker + Caddy and runs the server image. Caddy fetches a
  # Let's Encrypt cert for var.domain and reverse-proxies to the container.
  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    container_image = var.container_image
    domain          = var.domain
  })

  tags = var.tags
}

# Static IP so the DNS A record never changes across instance replacements.
resource "aws_lightsail_static_ip" "this" {
  name = "${var.name}-static-ip"
}

resource "aws_lightsail_static_ip_attachment" "this" {
  static_ip_name = aws_lightsail_static_ip.this.name
  instance_name  = aws_lightsail_instance.this.name
}

# Open only SSH (from operator IP), HTTP, and HTTPS.
resource "aws_lightsail_instance_public_ports" "this" {
  instance_name = aws_lightsail_instance.this.name

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
    cidrs     = [var.ssh_ingress_cidr]
  }

  port_info {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80
  }

  port_info {
    protocol  = "tcp"
    from_port = 443
    to_port   = 443
  }
}
