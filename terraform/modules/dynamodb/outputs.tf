output "raw_table_name" {
  description = "Name of the raw images DynamoDB table"
  value       = aws_dynamodb_table.raw_images.name
}

output "raw_table_arn" {
  description = "ARN of the raw images DynamoDB table"
  value       = aws_dynamodb_table.raw_images.arn
}

output "processed_table_name" {
  description = "Name of the processed images DynamoDB table"
  value       = aws_dynamodb_table.processed_images.name
}

output "processed_table_arn" {
  description = "ARN of the processed images DynamoDB table"
  value       = aws_dynamodb_table.processed_images.arn
}
