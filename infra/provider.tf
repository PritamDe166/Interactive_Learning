terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-south-2"

  default_tags {
    tags = {
      Project     = "InteractiveLearning"
      Environment = "development"
      ManagedBy   = "Terraform"
    }
  }
}

# CloudFront only accepts ACM certificates from us-east-1
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "InteractiveLearning"
      Environment = "development"
      ManagedBy   = "Terraform"
    }
  }
}
