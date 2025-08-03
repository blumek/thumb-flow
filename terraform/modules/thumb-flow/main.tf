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

# Dodanie kolejki SQS dla zdarzeń generowania miniatur
module "thumbnail_generation_queue" {
  source = "../sqs"

  queue_name                  = var.thumbnail_generation_queue_name
  visibility_timeout_seconds  = 120  # Dopasowany do timeoutu lambdy
  message_retention_seconds   = 86400  # 1 dzień
  tags                        = merge(var.tags, { Environment = var.environment })
}

module "upload_function" {
  source = "../lambda"

  function_name = var.upload_handler_function_name
  image_uri     = var.upload_handler_image_uri
  timeout       = 60
  memory_size   = 256

  environment_variables = {
    AWS_S3_BUCKET_NAME     = module.raw_images_bucket.bucket_name
    AWS_SQS_QUEUE_URL      = module.thumbnail_generation_queue.queue_url
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
    AWS_S3_RAW_BUCKET_NAME       = module.raw_images_bucket.bucket_name
    AWS_S3_THUMBNAIL_BUCKET_NAME = module.thumbnail_bucket.bucket_name
    AWS_SQS_QUEUE_URL            = module.thumbnail_generation_queue.queue_url
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

# Uprawnienia do publikowania wiadomości do SQS dla funkcji upload_handler
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

# Uprawnienia do odczytywania wiadomości z SQS dla funkcji thumbnail_generator
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

# Konfiguracja wyzwalacza SQS dla funkcji generującej miniatury
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
