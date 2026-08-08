output "vpc_id" {
  description = "ID of the VPC."
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs, ordered by AZ."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs, ordered by AZ."
  value       = aws_subnet.private[*].id
}

output "public_route_table_id" {
  description = "Shared public route table ID."
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "Per-AZ private route table IDs (nat-bastion adds the NAT default route to these)."
  value       = aws_route_table.private[*].id
}
