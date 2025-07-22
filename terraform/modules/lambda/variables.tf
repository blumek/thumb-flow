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