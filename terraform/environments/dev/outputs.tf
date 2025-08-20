output "raw_bucket_name" {
  description = "Name of the S3 bucket for raw images"
  value       = module.thumb_flow.raw_bucket_name
}

output "thumbnail_bucket_name" {
  description = "Name of the S3 bucket for thumbnail images"
  value       = module.thumb_flow.thumbnail_bucket_name
}

output "upload_function_name" {
  description = "Name of the Lambda function handling uploads"
  value       = module.thumb_flow.upload_function_name
}

output "thumbnail_generator_function_name" {
  description = "Name of the Lambda function generating thumbnails"
  value       = module.thumb_flow.thumbnail_generator_function_name
}

output "api_gateway_url" {
  description = "Base URL of the API Gateway"
  value       = module.thumb_flow.api_gateway_url
}

output "upload_api_endpoint" {
  description = "Complete URL for the upload endpoint"
  value       = module.thumb_flow.upload_api_endpoint
}

output "api_routes" {
  description = "Map of all API routes and their complete URLs"
  value       = module.thumb_flow.api_routes
}
