variable "function_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "image_uri" {
  description = "The URI of the container image for the Lambda function"
  type        = string
}

variable "timeout" {
  description = "The timeout for the Lambda function in seconds"
  type        = number
  default     = 5
}

variable "memory_size" {
  description = "The amount of memory available to the Lambda function in MB"
  type        = number
  default     = 128
}

variable "environment_variables" {
  description = "A map of environment variables to set for the Lambda function"
  type = map(string)
  default = {}
}

variable "tags" {
  description = "A map of tags to apply to the Lambda function"
  type = map(string)
  default = {}
}

variable "s3_events_permissions" {
  description = "ARNs of S3 buckets to grant permissions for Lambda function to access"
  type        = string
  default     = null
}

variable "enable_s3_output_policy" {
  description = "Enable S3 output policy for the Lambda function"
  type        = bool
  default     = false
}

variable "s3_output_bucket_arn" {
  description = "ARN of the S3 bucket for output permissions"
  type        = string
  default     = ""
}

variable "enable_dlq" {
  description = "Enable Dead Letter Queue for the Lambda function"
  type        = bool
  default     = true
}

variable "dlq_target_arn" {
  description = "ARN of the SQS queue or SNS topic for Dead Letter Queue"
  type        = string
  default     = null
}

variable "enable_xray_tracing" {
  description = "Enable X-Ray tracing for the Lambda function"
  type        = bool
  default     = false
}

variable "enable_vpc_config" {
  description = "Enable VPC configuration for the Lambda function"
  type        = bool
  default     = false
}

variable "vpc_subnet_ids" {
  description = "List of subnet IDs for VPC configuration"
  type        = list(string)
  default     = []
}

variable "vpc_security_group_ids" {
  description = "List of security group IDs for VPC configuration"
  type        = list(string)
  default     = []
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for environment variable encryption"
  type        = string
  default     = null
}

variable "reserved_concurrent_executions" {
  description = "Reserved concurrent executions for the Lambda function"
  type        = number
  default     = null
}

variable "enable_code_signing" {
  description = "Enable code signing for the Lambda function"
  type        = bool
  default     = false
}

variable "code_signing_config_arn" {
  description = "ARN of the code signing configuration"
  type        = string
  default     = null
}
