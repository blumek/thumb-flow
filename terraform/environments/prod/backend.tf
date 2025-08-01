terraform {
  backend "s3" {
    bucket = "infra-thumbflow-terraform-state"
    key    = "environments/prod/terraform.tfstate"
    region = "us-east-1"
  }
}