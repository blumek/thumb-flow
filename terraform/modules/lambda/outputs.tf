output "function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.this.function_name
}

output "function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.this.arn
}

output "role_arn" {
  description = "ARN of the IAM role used by the Lambda function"
  value       = aws_iam_role.lambda_execution_role.arn
}