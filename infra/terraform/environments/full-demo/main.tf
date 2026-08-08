# FULL-DEMO environment — the real VPC/EC2/NAT/bastion/EKS proof.
# BUILD -> RECORD -> DESTROY in a single session. Never leave applied.
#
#   terraform apply         # ~15 min (EKS is the slow part)
#   ...record the walkthrough...
#   terraform destroy       # or infra/scripts/destroy-full-demo.sh

# Latest Amazon Linux 2023 x86_64 AMI, resolved from the public SSM parameter.
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# ---- Network --------------------------------------------------------------
module "vpc" {
  source = "../../modules/vpc"

  name                 = "stocksense-demo"
  cidr_block           = var.vpc_cidr
  azs                  = var.azs
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "nat_bastion" {
  source = "../../modules/nat-bastion"

  name                    = "stocksense-demo"
  vpc_id                  = module.vpc.vpc_id
  public_subnet_id        = module.vpc.public_subnet_ids[0]
  private_route_table_ids = module.vpc.private_route_table_ids
  ssh_ingress_cidr        = var.ssh_ingress_cidr
  ami_id                  = data.aws_ssm_parameter.al2023.value
  key_name                = var.key_name
}

# ---- IAM: instance profile so the app host can pull from ECR --------------
data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app" {
  name               = "stocksense-demo-app-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

resource "aws_iam_role_policy_attachment" "app_ecr" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "app" {
  name = "stocksense-demo-app-profile"
  role = aws_iam_role.app.name
}

# ---- Raw EC2 app host in a private subnet (bastion-gated) -----------------
module "app_ec2" {
  source = "../../modules/ec2"

  name                      = "stocksense-demo"
  vpc_id                    = module.vpc.vpc_id
  vpc_cidr_block            = var.vpc_cidr
  subnet_id                 = module.vpc.private_subnet_ids[0]
  bastion_security_group_id = module.nat_bastion.bastion_security_group_id
  ami_id                    = data.aws_ssm_parameter.al2023.value
  instance_type             = var.app_instance_type
  container_image           = var.container_image
  ecr_registry              = var.ecr_registry
  region                    = var.region
  iam_instance_profile      = aws_iam_instance_profile.app.name
  key_name                  = var.key_name
}

# ---- EKS cluster (the Kubernetes proof) -----------------------------------
module "eks" {
  source = "../../modules/eks"

  name               = "stocksense-demo"
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
}

# ---- Handy outputs for the recording session ------------------------------
output "bastion_public_ip" {
  value       = module.nat_bastion.bastion_public_ip
  description = "SSH here first, then hop to the app host's private IP."
}

output "app_private_ip" {
  value       = module.app_ec2.private_ip
  description = "Raw EC2 app host, reachable from the bastion."
}

output "eks_cluster_name" {
  value       = module.eks.cluster_name
  description = "Run: aws eks update-kubeconfig --name <this> --region <region>"
}
