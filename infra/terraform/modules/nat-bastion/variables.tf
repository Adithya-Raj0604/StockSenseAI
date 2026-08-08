variable "name" {
  description = "Name prefix for NAT/bastion resources."
  type        = string
}

variable "vpc_id" {
  description = "VPC to attach the bastion security group to."
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet that hosts the NAT gateway and the bastion."
  type        = string
}

variable "private_route_table_ids" {
  description = "Private route tables that should egress through the NAT gateway."
  type        = list(string)
}

variable "ssh_ingress_cidr" {
  description = "CIDR allowed to SSH to the bastion (your IP as a /32)."
  type        = string
}

variable "ami_id" {
  description = "AMI for the bastion host."
  type        = string
}

variable "bastion_instance_type" {
  description = "Bastion instance type."
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "EC2 key pair name for SSH access to the bastion."
  type        = string
}

variable "tags" {
  description = "Extra tags merged onto every resource."
  type        = map(string)
  default     = {}
}
