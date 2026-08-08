variable "name" {
  description = "Name prefix for all VPC resources (e.g. stocksense-demo)."
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC (e.g. 10.0.0.0/16)."
  type        = string
}

variable "azs" {
  description = "Availability zones to spread subnets across. Subnet CIDR lists must match this length."
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "One public subnet CIDR per AZ."
  type        = list(string)

  validation {
    condition     = length(var.public_subnet_cidrs) == length(var.azs)
    error_message = "public_subnet_cidrs must have exactly one entry per AZ."
  }
}

variable "private_subnet_cidrs" {
  description = "One private subnet CIDR per AZ."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_cidrs) == length(var.azs)
    error_message = "private_subnet_cidrs must have exactly one entry per AZ."
  }
}

variable "tags" {
  description = "Extra tags merged onto every resource."
  type        = map(string)
  default     = {}
}
