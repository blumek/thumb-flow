resource "aws_dynamodb_table" "raw_images" {
  name         = var.raw_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "workflow_id"
    type = "S"
  }

  global_secondary_index {
    name            = "workflow-id-index"
    hash_key        = "workflow_id"
    projection_type = "ALL"
  }

  tags = var.tags
}

resource "aws_dynamodb_table" "processed_images" {
  name         = var.processed_table_name
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "workflow_id"
    type = "S"
  }

  global_secondary_index {
    name            = "workflow-id-index"
    hash_key        = "workflow_id"
    projection_type = "ALL"
  }

  tags = var.tags
}
