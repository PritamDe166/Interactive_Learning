terraform {
  backend "s3" {
    bucket       = "interactive-learning-terraform-state-951614973911-ap-south-2-an"
    key          = "interactive-learning/terraform.tfstate"
    region       = "ap-south-2"
    encrypt      = true
    use_lockfile = true
  }
}