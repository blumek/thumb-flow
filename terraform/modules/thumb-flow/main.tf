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

module "thumbnail_generation_queue" {
  source = "../sqs"

  queue_name                 = var.thumbnail_generation_queue_name
  visibility_timeout_seconds = 120   # Dopasowany do timeoutu lambdy
  message_retention_seconds  = 86400 # 1 dzień
  tags                       = merge(var.tags, { Environment = var.environment })
}

module "dynamodb" {
  source = "../dynamodb"

  raw_table_name       = var.raw_images_table_name
  processed_table_name = var.processed_images_table_name
  tags                 = merge(var.tags, { Environment = var.environment })
}

module "upload_function" {
  source = "../lambda"

  function_name = var.upload_handler_function_name
  image_uri     = var.upload_handler_image_uri
  timeout       = 60
  memory_size   = 256

  environment_variables = {
    AWS_S3_BUCKET_NAME        = module.raw_images_bucket.bucket_name
    AWS_SQS_QUEUE_URL         = module.thumbnail_generation_queue.queue_url
    AWS_DDB_RAW_TABLE_NAME    = module.dynamodb.raw_table_name
    AWS_DDB_PROCESSED_TABLE_NAME = module.dynamodb.processed_table_name
  }

  enable_s3_output_policy = true
  s3_output_bucket_arn    = module.raw_images_bucket.bucket_arn

  tags = merge(var.tags, { Environment = var.environment })
}

module "thumbnail_generator_function" {
  source = "../lambda"

  function_name = var.thumbnail_generator_function_name
  image_uri     = var.thumbnail_generator_image_uri
  timeout       = 120
  memory_size   = 512

  environment_variables = {
    AWS_S3_RAW_BUCKET_NAME          = module.raw_images_bucket.bucket_name
    AWS_S3_THUMBNAIL_BUCKET_NAME    = module.thumbnail_bucket.bucket_name
    AWS_SQS_QUEUE_URL               = module.thumbnail_generation_queue.queue_url
    AWS_DDB_RAW_TABLE_NAME          = module.dynamodb.raw_table_name
    AWS_DDB_PROCESSED_TABLE_NAME    = module.dynamodb.processed_table_name
  }

  enable_s3_output_policy = true
  s3_output_bucket_arn    = module.raw_images_bucket.bucket_arn

  tags = merge(var.tags, { Environment = var.environment })
}

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

resource "aws_iam_policy" "upload_function_sqs_publish" {
  name        = "${var.upload_handler_function_name}-sqs-publish-policy"
  description = "Allows upload Lambda function to publish messages to SQS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:SendMessage",
          "sqs:GetQueueUrl",
          "sqs:GetQueueAttributes"
        ]
        Effect   = "Allow"
        Resource = module.thumbnail_generation_queue.queue_arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "upload_function_sqs_publish" {
  role       = module.upload_function.execution_role_name
  policy_arn = aws_iam_policy.upload_function_sqs_publish.arn
}

resource "aws_iam_policy" "thumbnail_function_sqs_receive" {
  name        = "${var.thumbnail_generator_function_name}-sqs-receive-policy"
  description = "Allows thumbnail generator function to receive messages from SQS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueUrl",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Effect   = "Allow"
        Resource = module.thumbnail_generation_queue.queue_arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "thumbnail_function_sqs_receive" {
  role       = module.thumbnail_generator_function.execution_role_name
  policy_arn = aws_iam_policy.thumbnail_function_sqs_receive.arn
}

resource "aws_iam_policy" "dynamodb_access" {
  name        = "${var.environment}-thumbflow-dynamodb-access"
  description = "Permissions for Lambda functions to access DynamoDB tables"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
          "dynamodb:BatchGetItem",
          "dynamodb:DescribeTable"
        ]
        Resource = [
          module.dynamodb.raw_table_arn,
          "${module.dynamodb.raw_table_arn}/index/*",
          module.dynamodb.processed_table_arn,
          "${module.dynamodb.processed_table_arn}/index/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "upload_function_dynamodb_access" {
  role       = module.upload_function.execution_role_name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "thumbnail_function_dynamodb_access" {
  role       = module.thumbnail_generator_function.execution_role_name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_lambda_event_source_mapping" "thumbnail_generator_sqs_trigger" {
  event_source_arn = module.thumbnail_generation_queue.queue_arn
  function_name    = module.thumbnail_generator_function.function_arn
  batch_size       = 1
}

resource "aws_iam_policy" "bedrock_access" {
  name        = "${var.thumbnail_generator_function_name}-bedrock-access-policy"
  description = "Allows Lambda function to invoke Amazon Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "bedrock:InvokeModel",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_access" {
  role       = module.thumbnail_generator_function.execution_role_name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

module "api_gateway" {
  source = "../api-gateway"

  api_name            = "${var.environment}-thumbflow-api"
  description         = "API Gateway for ThumbFlow ${var.environment} environment"
  stage_name          = var.environment

  routes = [
    {
      path                = "/images"
      http_method         = "POST"
      lambda_function_name = module.upload_function.function_name
      lambda_invoke_arn   = module.upload_function.function_arn
      description         = "Upload images endpoint"
    }
  ]

  cors_allow_origins  = ["*"]
  cors_allow_methods  = ["GET", "POST", "PUT", "OPTIONS"]
  cors_allow_headers  = ["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key"]
  cors_allow_credentials = false

  use_custom_domain   = false

  throttling_burst_limit = 10
  throttling_rate_limit  = 5

  tags                = merge(var.tags, { Environment = var.environment })
}
