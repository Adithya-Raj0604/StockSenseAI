terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "StockSenseAI-Infra"
      Environment = "full-demo"
      ManagedBy   = "terraform"
    }
  }
}
