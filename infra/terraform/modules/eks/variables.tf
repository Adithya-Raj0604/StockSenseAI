variable "name" {
  description = "Cluster name / prefix."
  type        = string
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version."
  type        = string
  default     = "1.31"
}

variable "public_subnet_ids" {
  description = "Public subnets for the control-plane ENIs and public LoadBalancers."
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnets where worker nodes run."
  type        = list(string)
}

variable "node_instance_types" {
  description = "Instance types for the managed node group."
  type        = list(string)
  default     = ["t3.small"]
}

variable "capacity_type" {
  description = "ON_DEMAND or SPOT. SPOT is cheaper for a throwaway demo cluster."
  type        = string
  default     = "SPOT"
}

variable "desired_size" {
  description = "Desired node count."
  type        = number
  default     = 2
}

variable "min_size" {
  description = "Minimum node count."
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum node count."
  type        = number
  default     = 3
}

variable "tags" {
  description = "Extra tags merged onto every resource."
  type        = map(string)
  default     = {}
}
