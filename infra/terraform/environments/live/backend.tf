# State backend.
#
# Defaults to LOCAL state so `terraform init` works with no prerequisites.
# For a shared/CI setup, create an S3 bucket + DynamoDB lock table (kept
# entirely separate from anything the SAM/CloudFormation stack manages) and
# uncomment the block below.
#
# terraform {
#   backend "s3" {
#     bucket         = "stocksense-infra-tfstate"
#     key            = "live/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "stocksense-infra-tflock"
#     encrypt        = true
#   }
# }
