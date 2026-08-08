output "private_ip" {
  description = "Private IP of the app instance (reach it from the bastion)."
  value       = aws_instance.app.private_ip
}

output "instance_id" {
  description = "App instance ID."
  value       = aws_instance.app.id
}

output "security_group_id" {
  description = "App instance security group ID."
  value       = aws_security_group.app.id
}
