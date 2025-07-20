output "raw_bucket_name" {
  description = "Name of the S3 bucket for raw images"
  value       = module.thumb_flow.raw_bucket_name
}

output "upload_function_name" {
  description = "Name of the Lambda function handling uploads"
  value       = module.thumb_flow.upload_function_name
}