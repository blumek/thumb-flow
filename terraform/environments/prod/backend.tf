terraform {
  backend "s3" {
    bucket = "thumbflow-terraform-state"
    key    = "environments/prod/terraform.tfstate"
    region = "eu-central-1"
  }
}