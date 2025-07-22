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

variable "enable_lifecycle_configuration" {
  description = "Enable S3 bucket lifecycle configuration"
  type        = bool
  default     = true
}

variable "lifecycle_rules" {
  description = "List of lifecycle rules"
  type = list(object({
    id     = string
    status = string
    expiration_days = optional(number)
    noncurrent_version_expiration_days = optional(number)
    abort_incomplete_multipart_upload_days = optional(number)
  }))
  default = [
    {
      id              = "default"
      status          = "Enabled"
      expiration_days = 90
      noncurrent_version_expiration_days = 30
      abort_incomplete_multipart_upload_days = 7
    }
  ]
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
