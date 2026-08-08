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

  # Every resource created here is tagged for isolated billing / cleanup,
  # separate from the existing Lambda/SAM deployment.
  default_tags {
    tags = {
      Project     = "StockSenseAI-Infra"
      Environment = "live"
      ManagedBy   = "terraform"
    }
  }
}
