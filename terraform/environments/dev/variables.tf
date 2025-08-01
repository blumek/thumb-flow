variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "eu-central-1"
}

variable "upload_handler_image_uri" {
  description = "URI of the ECR image for the upload handler Lambda function"
  type        = string
}

variable "thumbnail_generator_image_uri" {
  description = "URI of the ECR image for the thumbnail generator Lambda function"
  type        = string
}
