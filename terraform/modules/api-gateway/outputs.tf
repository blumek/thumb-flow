output "api_id" {
  description = "ID of the API Gateway"
  value       = aws_apigatewayv2_api.this.id
}

output "api_endpoint" {
  description = "HTTP API Gateway endpoint"
  value       = aws_apigatewayv2_api.this.api_endpoint
}

output "stage_endpoint" {
  description = "The complete URL to invoke the API at the stage"
  value       = aws_apigatewayv2_stage.this.invoke_url
}

output "execution_arn" {
  description = "The execution ARN of the API Gateway"
  value       = aws_apigatewayv2_api.this.execution_arn
}

output "route_endpoints" {
  description = "Map of complete URLs for each route in the API"
  value       = { for idx, route in var.routes : route.path => "${aws_apigatewayv2_stage.this.invoke_url}${route.path}" }
}

output "upload_endpoint" {
  description = "The complete URL for the upload endpoint (first route in the routes list for backward compatibility)"
  value       = length(var.routes) > 0 ? "${aws_apigatewayv2_stage.this.invoke_url}${var.routes[0].path}" : null
}
