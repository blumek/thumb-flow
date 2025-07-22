module "raw_images_bucket" {
  source = "../s3"

  bucket_name = var.raw_bucket_name
  tags = merge(var.tags, { Environment = var.environment })

  enable_notification = false

  # Security configurations
  enable_access_logging = var.enable_access_logging
  logging_bucket = var.logging_bucket
  enable_lifecycle_configuration = true
  enable_cross_region_replication = var.enable_cross_region_replication
  replication_bucket_arn = var.replication_bucket_arn
  replication_role_arn = var.replication_role_arn
}

# Create SQS queue for Lambda DLQ
resource "aws_sqs_queue" "lambda_dlq" {
  name = "${var.upload_handler_function_name}-dlq"

  message_retention_seconds = 1209600 # 14 days
  kms_master_key_id = "alias/aws/sqs"  # Enable encryption

  tags = merge(var.tags, { Environment = var.environment })
}

module "upload_function" {
  source = "../lambda"

  function_name = var.upload_handler_function_name
  image_uri     = var.upload_handler_image_uri
  timeout       = 60
  memory_size   = 256

  environment_variables = {
    AWS_S3_BUCKET_NAME = module.raw_images_bucket.bucket_name
  }

  enable_s3_output_policy = true
  s3_output_bucket_arn    = module.raw_images_bucket.bucket_arn

  # DLQ configuration
  enable_dlq = true
  dlq_target_arn = aws_sqs_queue.lambda_dlq.arn

  # Security configurations
  enable_xray_tracing = var.enable_lambda_xray_tracing
  reserved_concurrent_executions = var.lambda_reserved_concurrent_executions

  tags = merge(var.tags, { Environment = var.environment })
}