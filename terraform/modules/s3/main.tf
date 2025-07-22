resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_ownership_controls" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "this" {
  count  = var.enable_access_logging && var.logging_bucket != null ? 1 : 0
  bucket = aws_s3_bucket.this.id

  target_bucket = var.logging_bucket
  target_prefix = "access-logs/${var.bucket_name}/"
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  count  = var.enable_lifecycle_configuration ? 1 : 0
  bucket = aws_s3_bucket.this.id

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.status

      dynamic "abort_incomplete_multipart_upload" {
        for_each = rule.value.abort_incomplete_multipart_upload_days != null ? [1] : []
        content {
          days_after_initiation = rule.value.abort_incomplete_multipart_upload_days
        }
      }

      dynamic "expiration" {
        for_each = rule.value.expiration_days != null ? [1] : []
        content {
          days = rule.value.expiration_days
        }
      }

      dynamic "noncurrent_version_expiration" {
        for_each = rule.value.noncurrent_version_expiration_days != null ? [1] : []
        content {
          noncurrent_days = rule.value.noncurrent_version_expiration_days
        }
      }
    }
  }

  depends_on = [aws_s3_bucket_versioning.this]
}

resource "aws_s3_bucket_replication_configuration" "this" {
  count  = var.enable_cross_region_replication && var.replication_bucket_arn != null ? 1 : 0
  role   = var.replication_role_arn
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "replicate-everything"
    status = "Enabled"

    destination {
      bucket        = var.replication_bucket_arn
      storage_class = "STANDARD_IA"
    }
  }

  depends_on = [aws_s3_bucket_versioning.this]
}

resource "aws_s3_bucket_notification" "this" {
  count  = var.enable_notification ? 1 : 0
  bucket = aws_s3_bucket.this.id

  lambda_function {
    lambda_function_arn = var.notification_lambda_arn
    events = ["s3:ObjectCreated:*"]
  }
}