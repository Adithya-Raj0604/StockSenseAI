# NAT gateway (egress for private subnets) + bastion host (SSH entry point).
# This is the *paid* part of the network — a single NAT gateway is ~$32/mo, so
# this module is only ever applied in the ephemeral full-demo environment.

# ---- NAT gateway ----------------------------------------------------------
# One NAT in a single public subnet (cost-conscious; prod would run one per AZ).
resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.name}-nat-eip" })
}

resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = var.public_subnet_id
  tags          = merge(var.tags, { Name = "${var.name}-nat" })
}

# Default route out of each private subnet through the NAT gateway.
resource "aws_route" "private_nat" {
  count                  = length(var.private_route_table_ids)
  route_table_id         = var.private_route_table_ids[count.index]
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this.id
}

# ---- Bastion host ---------------------------------------------------------
resource "aws_security_group" "bastion" {
  name        = "${var.name}-bastion-sg"
  description = "Bastion: SSH in from operator IP only, all egress."
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from operator IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_ingress_cidr]
  }

  egress {
    description = "All egress"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.name}-bastion-sg" })
}

resource "aws_instance" "bastion" {
  ami                    = var.ami_id
  instance_type          = var.bastion_instance_type
  subnet_id              = var.public_subnet_id
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.bastion.id]

  tags = merge(var.tags, { Name = "${var.name}-bastion" })
}
