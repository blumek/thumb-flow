variable "raw_table_name" {
  description = "Name of the DynamoDB table for raw images"
  type        = string
}

variable "processed_table_name" {
  description = "Name of the DynamoDB table for processed images"
  type        = string
}

variable "tags" {
  description = "Tags to apply to DynamoDB tables"
  type        = map(string)
  default     = {}
}
