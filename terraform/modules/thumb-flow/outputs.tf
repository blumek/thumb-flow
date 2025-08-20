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

output "api_routes" {
  description = "Map of all API routes and their complete URLs"
  value       = module.api_gateway.route_endpoints
}

output "raw_images_table_name" {
  description = "Name of the DynamoDB RawImages table"
  value       = module.dynamodb.raw_table_name
}

output "processed_images_table_name" {
  description = "Name of the DynamoDB ProcessedImages table"
  value       = module.dynamodb.processed_table_name
}
