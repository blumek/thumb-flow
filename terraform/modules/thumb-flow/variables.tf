variable "environment" {
  description = "Environment for the Lambda application (e.g., dev, prod)"
  type        = string
}

variable "raw_bucket_name" {
  description = "Name of the S3 bucket for raw images"
  type        = string
}

variable "thumbnail_bucket_name" {
  description = "Name of the S3 bucket for thumbnail images"
  type        = string
}

variable "thumbnail_generation_queue_name" {
  description = "Name of the SQS queue for thumbnail generation events"
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

variable "thumbnail_generator_function_name" {
  description = "Name of the Lambda function generating thumbnails"
  type        = string
}

variable "thumbnail_generator_image_uri" {
  description = "URI of the ECR image for the thumbnail generator Lambda function"
  type        = string
}

variable "raw_images_table_name" {
  description = "Name of the DynamoDB table for raw images"
  type        = string
}

variable "processed_images_table_name" {
  description = "Name of the DynamoDB table for processed images"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the Lambda functions and S3 buckets"
  type        = map(string)
  default     = {}
}

variable "cors_allow_origins" {
  description = "List of allowed origins for CORS in API Gateway"
  type        = list(string)
  default     = ["*"]
}
