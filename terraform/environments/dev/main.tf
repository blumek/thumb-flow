provider "aws" {
  region = var.aws_region
}

module "thumb_flow" {
  source = "../../modules/thumb-flow"

  environment                  = "dev"
  raw_bucket_name              = "thumbflow-raw-images-dev"
  upload_handler_function_name = "thumbflow-upload-handler-dev"
  upload_handler_image_uri     = var.upload_handler_image_uri

  # Security configurations for dev environment
  enable_access_logging = false  # Disabled for dev to save costs
  logging_bucket = null
  enable_cross_region_replication = false  # Not needed for dev

  tags = {
    Project     = "ThumbFlow"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}