provider "aws" {
  region = var.aws_region
}

module "thumb_flow" {
  source = "../../modules/thumb-flow"

  environment                       = "dev"
  raw_bucket_name                   = "thumbflow-raw-images-bucket-dev"
  thumbnail_bucket_name             = "thumbflow-thumbnails-bucket-dev"
  thumbnail_generation_queue_name   = "thumbflow-thumbnail-generation-queue-dev"
  upload_handler_function_name      = "thumbflow-upload-handler-dev"
  upload_handler_image_uri          = var.upload_handler_image_uri
  thumbnail_generator_function_name = "thumbflow-thumbnail-generator-dev"
  thumbnail_generator_image_uri     = var.thumbnail_generator_image_uri

  tags = {
    Project     = "ThumbFlow"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}