resource "aws_lambda_function" "this" {
  function_name = var.function_name
  package_type  = "Image"
  image_uri     = var.image_uri
  timeout       = var.timeout
  memory_size   = var.memory_size
  role          = aws_iam_role.lambda_execution_role.arn

  # Security configurations
  reserved_concurrent_executions = var.reserved_concurrent_executions
  kms_key_arn = var.kms_key_arn
  code_signing_config_arn = var.enable_code_signing && var.code_signing_config_arn != null ? var.code_signing_config_arn : null

  dynamic "dead_letter_config" {
    for_each = var.enable_dlq && var.dlq_target_arn != null ? [1] : []
    content {
      target_arn = var.dlq_target_arn
    }
  }

  dynamic "vpc_config" {
    for_each = var.enable_vpc_config ? [1] : []
    content {
      subnet_ids         = var.vpc_subnet_ids
      security_group_ids = var.vpc_security_group_ids
    }
  }

  dynamic "environment" {
    for_each = length(var.environment_variables) > 0 ? [1] : []
    content {
      variables = var.environment_variables
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  tags = var.tags
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.function_name}-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_permission" "s3_event" {
  count         = var.s3_events_permissions != null ? 1 : 0
  statement_id  = "AllowS3Invocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.s3_events_permissions
}

resource "aws_iam_policy" "s3_output" {
  count       = var.enable_s3_output_policy ? 1 : 0
  name        = "${var.function_name}-s3-output-policy"
  description = "Allows Lambda function to access S3 outputs"

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
        Resource = "${var.s3_output_bucket_arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_output" {
  count      = var.enable_s3_output_policy ? 1 : 0
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.s3_output[0].arn
}