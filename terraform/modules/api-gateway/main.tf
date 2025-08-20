resource "aws_apigatewayv2_api" "this" {
  name          = var.api_name
  protocol_type = "HTTP"
  description   = var.description

  cors_configuration {
    allow_origins     = var.cors_allow_origins
    allow_methods     = var.cors_allow_methods
    allow_headers     = var.cors_allow_headers
    allow_credentials = var.cors_allow_credentials
    max_age           = var.cors_max_age
    expose_headers    = var.cors_expose_headers
  }

  tags = var.tags
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = var.stage_name
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = var.throttling_burst_limit
    throttling_rate_limit  = var.throttling_rate_limit
  }

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      path           = "$context.path"
    })
  }

  tags = var.tags
}

resource "aws_apigatewayv2_api_mapping" "example" {
  count = var.use_custom_domain ? 1 : 0

  api_id      = aws_apigatewayv2_api.this.id
  domain_name = var.custom_domain_name
  stage       = aws_apigatewayv2_stage.this.id
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/api-gateway/${var.api_name}"
  retention_in_days = var.log_retention_in_days
  tags              = var.tags
}

resource "aws_apigatewayv2_integration" "lambda_integrations" {
  for_each = { for idx, route in var.routes : idx => route }

  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_uri        = each.value.lambda_invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = var.integration_timeout_milliseconds
  description            = each.value.description != null ? each.value.description : "Integration for ${each.value.path}"
}

resource "aws_apigatewayv2_route" "routes" {
  for_each = { for idx, route in var.routes : idx => route }

  api_id    = aws_apigatewayv2_api.this.id
  route_key = "${each.value.http_method} ${each.value.path}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integrations[each.key].id}"
}

resource "aws_lambda_permission" "api_gateway_invoke_lambda" {
  for_each = { for idx, route in var.routes : idx => route if route.lambda_function_name != null }

  statement_id  = "AllowExecutionFromAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*/*"
}
