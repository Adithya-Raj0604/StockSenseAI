output "bastion_public_ip" {
  description = "Public IP of the bastion host (SSH jump box)."
  value       = aws_instance.bastion.public_ip
}

output "bastion_security_group_id" {
  description = "Bastion SG ID — reference this as the SSH source for private instances."
  value       = aws_security_group.bastion.id
}

output "nat_gateway_id" {
  description = "NAT gateway ID."
  value       = aws_nat_gateway.this.id
}
