variable "api_name" {
  description = "Name of the API Gateway"
  type        = string
}

variable "description" {
  description = "Description of the API Gateway"
  type        = string
  default     = "API Gateway for application"
}

variable "stage_name" {
  description = "Name of the API Gateway stage"
  type        = string
  default     = "default"
}

variable "routes" {
  description = "List of route configurations for API Gateway"
  type = list(object({
    path                = string
    http_method         = string
    lambda_function_name = string
    lambda_invoke_arn   = string
    description         = optional(string)
  }))
}

variable "cors_allow_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allow_methods" {
  description = "List of allowed methods for CORS"
  type        = list(string)
  default     = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
}

variable "cors_allow_headers" {
  description = "List of allowed headers for CORS"
  type        = list(string)
  default     = ["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key", "X-Amz-Security-Token", "X-Amz-User-Agent"]
}

variable "cors_allow_credentials" {
  description = "Whether credentials are included in CORS"
  type        = bool
  default     = false
}

variable "cors_expose_headers" {
  description = "List of headers to expose in CORS response"
  type        = list(string)
  default     = ["Content-Length", "Content-Type"]
}

variable "cors_max_age" {
  description = "Max age for CORS in seconds"
  type        = number
  default     = 300
}

variable "use_custom_domain" {
  description = "Whether to use a custom domain for the API Gateway"
  type        = bool
  default     = false
}

variable "custom_domain_name" {
  description = "Custom domain name for API Gateway"
  type        = string
  default     = ""
}

variable "throttling_burst_limit" {
  description = "Throttling burst limit for API Gateway routes"
  type        = number
  default     = 5
}

variable "throttling_rate_limit" {
  description = "Throttling rate limit for API Gateway routes"
  type        = number
  default     = 10
}

variable "log_retention_in_days" {
  description = "Number of days to retain API Gateway logs"
  type        = number
  default     = 7
}

variable "integration_timeout_milliseconds" {
  description = "Timeout for the Lambda integration in milliseconds"
  type        = number
  default     = 30000 # 30 seconds
}

variable "tags" {
  description = "Tags to apply to the API Gateway resources"
  type        = map(string)
  default     = {}
}
