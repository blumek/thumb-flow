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

output "api_routes" {
  description = "Map of all API routes and their complete URLs"
  value       = module.thumb_flow.api_routes
}

output "raw_images_table_name" {
  description = "Name of the DynamoDB RawImages table"
  value       = module.thumb_flow.raw_images_table_name
}

output "processed_images_table_name" {
  description = "Name of the DynamoDB ProcessedImages table"
  value       = module.thumb_flow.processed_images_table_name
}
