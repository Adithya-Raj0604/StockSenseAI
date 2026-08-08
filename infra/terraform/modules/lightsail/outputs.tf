output "static_ip" {
  description = "Static public IP — create a DNS A record for var.domain pointing here."
  value       = aws_lightsail_static_ip.this.ip_address
}

output "instance_name" {
  description = "Lightsail instance name."
  value       = aws_lightsail_instance.this.name
}
