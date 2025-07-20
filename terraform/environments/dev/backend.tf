terraform {
  backend "s3" {
    bucket = "thumbflow-terraform-state"
    key    = "environments/dev/terraform.tfstate"
    region = "eu-central-1"
  }
}