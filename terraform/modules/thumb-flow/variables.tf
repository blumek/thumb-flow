variable "environment" {
  description = "Environment for the Lambda application (e.g., dev, prod)"
  type        = string
}

variable "raw_bucket_name" {
  description = "Name of the S3 bucket for raw images"
  type        = string
}

variable "upload_handler_function_name" {
  description = "Name of the Lambda function handling uploads"
  type        = string
}

variable "upload_handler_image_uri" {
  description = "URI of the ECR image for the upload handler Lambda function"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the Lambda functions and S3 buckets"
  type = map(string)
  default = {}
}

variable "enable_access_logging" {
  description = "Enable S3 bucket access logging"
  type        = bool
  default     = true
}

variable "logging_bucket" {
  description = "The S3 bucket to store access logs"
  type        = string
  default     = null
}

variable "enable_cross_region_replication" {
  description = "Enable S3 bucket cross-region replication"
  type        = bool
  default     = false
}

variable "replication_bucket_arn" {
  description = "The ARN of the destination bucket for cross-region replication"
  type        = string
  default     = null
}

variable "replication_role_arn" {
  description = "The ARN of the IAM role for cross-region replication"
  type        = string
  default     = null
}

variable "enable_lambda_xray_tracing" {
  description = "Enable X-Ray tracing for Lambda functions"
  type        = bool
  default     = false
}

variable "lambda_reserved_concurrent_executions" {
  description = "Reserved concurrent executions for Lambda functions"
  type        = number
  default     = 10
}
