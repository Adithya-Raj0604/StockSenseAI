variable "region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "azs" {
  description = "Two AZs for the multi-AZ VPC."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "vpc_cidr" {
  description = "VPC CIDR."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "One per AZ."
  type        = list(string)
  default     = ["10.0.0.0/24", "10.0.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "One per AZ."
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "ssh_ingress_cidr" {
  description = "Your IP as a /32 for bastion SSH."
  type        = string
}

variable "key_name" {
  description = "Existing EC2 key pair name for SSH access."
  type        = string
}

variable "container_image" {
  description = "ECR image reference built from backend/Dockerfile.server."
  type        = string
}

variable "ecr_registry" {
  description = "ECR registry host, e.g. 123456789012.dkr.ecr.us-east-1.amazonaws.com."
  type        = string
}

variable "app_instance_type" {
  description = "Instance type for the raw EC2 app host."
  type        = string
  default     = "t3.small"
}
