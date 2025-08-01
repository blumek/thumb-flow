terraform {
  backend "s3" {
    bucket = "infra-thumbflow-terraform-state"
    key    = "environments/dev/terraform.tfstate"
    region = "us-east-1"
  }
}