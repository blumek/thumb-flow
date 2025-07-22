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