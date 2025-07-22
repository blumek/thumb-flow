variable "bucket_name" {
  description = "The name of the S3 bucket to create"
  type        = string
}

variable "tags" {
  description = "A map of tags to apply to the S3 bucket"
  type = map(string)
  default = {}
}

variable "enable_notification" {
  description = "Enable S3 bucket notification configuration"
  type        = bool
  default     = false
}

variable "notification_lambda_arn" {
  description = "The ARN of the Lambda function to notify"
  type        = string
  default     = null
}