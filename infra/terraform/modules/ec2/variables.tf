variable "name" {
  description = "Name prefix for the app instance resources."
  type        = string
}

variable "vpc_id" {
  description = "VPC to attach the app security group to."
  type        = string
}

variable "vpc_cidr_block" {
  description = "VPC CIDR — used to allow the app port from within the VPC only."
  type        = string
}

variable "subnet_id" {
  description = "PRIVATE subnet to place the instance in."
  type        = string
}

variable "bastion_security_group_id" {
  description = "Bastion SG allowed to SSH into this instance."
  type        = string
}

variable "ami_id" {
  description = "AMI for the app instance (Amazon Linux 2023 recommended)."
  type        = string
}

variable "instance_type" {
  description = "Instance type for the app host."
  type        = string
  default     = "t3.small"
}

variable "app_port" {
  description = "Host port to expose the container on."
  type        = number
  default     = 8000
}

variable "container_image" {
  description = "Full image reference to run (ECR repo:tag built from backend/Dockerfile.server)."
  type        = string
}

variable "ecr_registry" {
  description = "ECR registry host (<account>.dkr.ecr.<region>.amazonaws.com) for docker login."
  type        = string
}

variable "region" {
  description = "AWS region (used by user-data for ECR login)."
  type        = string
}

variable "iam_instance_profile" {
  description = "Instance profile granting ECR pull access."
  type        = string
}

variable "key_name" {
  description = "EC2 key pair name for SSH (via bastion)."
  type        = string
}

variable "tags" {
  description = "Extra tags merged onto every resource."
  type        = map(string)
  default     = {}
}
