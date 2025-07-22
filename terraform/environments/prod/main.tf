provider "aws" {
  region = var.aws_region
}

module "thumb_flow" {
  source = "../../modules/thumb-flow"

  environment                  = "prod"
  raw_bucket_name              = "thumbflow-raw-images-prod"
  upload_handler_function_name = "thumbflow-upload-handler-prod"
  upload_handler_image_uri     = var.upload_handler_image_uri

  tags = {
    Project     = "ThumbFlow"
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}