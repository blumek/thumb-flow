module "raw_images_bucket" {
  source = "../s3"

  bucket_name = var.raw_bucket_name
  tags        = merge(var.tags, { Environment = var.environment })
}

module "thumbnail_bucket" {
  source = "../s3"

  bucket_name = var.thumbnail_bucket_name
  tags        = merge(var.tags, { Environment = var.environment })
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

module "thumbnail_generator_function" {
  source = "../lambda"

  function_name = var.thumbnail_generator_function_name
  image_uri     = var.thumbnail_generator_image_uri
  timeout       = 120 # Zwiększony timeout dla przetwarzania obrazów
  memory_size   = 512 # Zwiększona pamięć dla operacji na obrazach

  environment_variables = {
    RAW_S3_BUCKET_NAME       = module.raw_images_bucket.bucket_name
    THUMBNAIL_S3_BUCKET_NAME = module.thumbnail_bucket.bucket_name
  }

  # Uprawnienia do odczytu z bucketa z surowymi obrazami
  enable_s3_output_policy = true
  s3_output_bucket_arn    = module.raw_images_bucket.bucket_arn

  tags = merge(var.tags, { Environment = var.environment })
}

# Dodatkowa polityka dla dostępu do bucketa z miniaturami
resource "aws_iam_policy" "thumbnail_bucket_access" {
  name        = "${var.thumbnail_generator_function_name}-thumbnail-bucket-policy"
  description = "Allows Lambda function to access thumbnail S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = "${module.thumbnail_bucket.bucket_arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "thumbnail_bucket_access" {
  role       = module.thumbnail_generator_function.execution_role_name
  policy_arn = aws_iam_policy.thumbnail_bucket_access.arn
}
