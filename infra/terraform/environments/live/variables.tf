variable "region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "availability_zone" {
  description = "AZ for the Lightsail instance."
  type        = string
  default     = "us-east-1a"
}

variable "container_image" {
  description = "ECR image reference built from backend/Dockerfile.server."
  type        = string
}

variable "domain" {
  description = "Subdomain for the live host (e.g. selfhosted.example.com). Point its A record at the module's static_ip output."
  type        = string
}

variable "ssh_ingress_cidr" {
  description = "Your IP as a /32 for SSH (e.g. 203.0.113.4/32)."
  type        = string
}

variable "bundle_id" {
  description = "Lightsail bundle. small_3_0 = 1 GB (~$5/mo, recommended)."
  type        = string
  default     = "small_3_0"
}
