provider "aws" {
  region = var.aws_region
}

# Create logging bucket for prod environment
resource "aws_s3_bucket" "access_logs" {
  bucket = "thumbflow-access-logs-prod"

  tags = {
    Project     = "ThumbFlow"
    Environment = "prod"
    ManagedBy   = "terraform"
    Purpose     = "access-logs"
  }
}

resource "aws_s3_bucket_public_access_block" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

module "thumb_flow" {
  source = "../../modules/thumb-flow"

  environment                  = "prod"
  raw_bucket_name              = "thumbflow-raw-images-prod"
  upload_handler_function_name = "thumbflow-upload-handler-prod"
  upload_handler_image_uri     = var.upload_handler_image_uri

  # Security configurations for prod environment
  enable_access_logging = true
  logging_bucket = aws_s3_bucket.access_logs.id
  enable_cross_region_replication = false  # Can be enabled if needed

  # Lambda security configurations
  enable_lambda_xray_tracing = true
  lambda_reserved_concurrent_executions = 50  # Higher limit for prod

  tags = {
    Project     = "ThumbFlow"
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}