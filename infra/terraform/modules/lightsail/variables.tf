variable "name" {
  description = "Lightsail instance name."
  type        = string
}

variable "availability_zone" {
  description = "AZ for the instance (e.g. us-east-1a)."
  type        = string
}

variable "blueprint_id" {
  description = "OS blueprint (e.g. amazon_linux_2023)."
  type        = string
  default     = "amazon_linux_2023"
}

variable "bundle_id" {
  description = "Lightsail bundle. small_3_0 = 1 GB (~$5/mo). nano_3_0 = 512 MB (~$3.50) likely OOMs the model."
  type        = string
  default     = "small_3_0"
}

variable "container_image" {
  description = "Full image reference to run (ECR repo:tag from backend/Dockerfile.server)."
  type        = string
}

variable "domain" {
  description = "Subdomain Caddy will fetch a TLS cert for (e.g. selfhosted.example.com). Point its A record at the static IP."
  type        = string
}

variable "ssh_ingress_cidr" {
  description = "CIDR allowed to SSH (your IP as a /32)."
  type        = string
}

variable "tags" {
  description = "Extra tags merged onto the instance."
  type        = map(string)
  default     = {}
}
