output "raw_bucket_name" {
  description = "Name of the S3 bucket for raw images"
  value       = module.raw_images_bucket.bucket_id
}

output "thumbnail_bucket_name" {
  description = "Name of the S3 bucket for thumbnail images"
  value       = module.thumbnail_bucket.bucket_id
}

output "upload_function_name" {
  description = "Name of the Lambda function handling uploads"
  value       = module.upload_function.function_name
}

output "thumbnail_generator_function_name" {
  description = "Name of the Lambda function generating thumbnails"
  value       = module.thumbnail_generator_function.function_name
}

output "api_gateway_url" {
  description = "Base URL of the API Gateway"
  value       = module.api_gateway.stage_endpoint
}

output "upload_api_endpoint" {
  description = "Complete URL for the upload endpoint"
  value       = module.api_gateway.upload_endpoint
}

output "api_routes" {
  description = "Map of all API routes and their complete URLs"
  value       = module.api_gateway.route_endpoints
}
