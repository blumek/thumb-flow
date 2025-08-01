terraform {
  backend "s3" {
    bucket = "thumbflow-terraform-state"
    key    = "environments/dev/terraform.tfstate"
    region = "us-east-1"
  }
}