module "raw_images_bucket" {
  source = "../s3"

  bucket_name = var.raw_bucket_name
  tags        = merge(var.tags, { Environment = var.environment })

  enable_notification = false
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

  tags = merge(var.tags, { Environment = var.environment })
}