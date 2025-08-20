plugins {
    id("com.github.psxpaul.execfork")
    id("com.blumek.thumbflow.localstack")
}

description = "AWS Lambda function for image resizing and thumbnail generation"

val testEnvironment = mapOf(
    "AWS_ACCESS_KEY_ID" to "test",
    "AWS_SECRET_ACCESS_KEY" to "test",
    "AWS_REGION" to "us-east-1",
    "AWS_S3_RAW_BUCKET_NAME" to "thumbnail-generator-raw-bucket",
    "AWS_S3_THUMBNAIL_BUCKET_NAME" to "thumbnail-generator-thumbnail-bucket",
    "AWS_ENDPOINT_URL" to "http://localhost:4567"
)

localStack {
    containerName.set("thumbnail-generator-localstack")
    port.set(4567)
    services.set("s3")
    region.set(testEnvironment["AWS_REGION"]!!)
    accessKeyId.set(testEnvironment["AWS_ACCESS_KEY_ID"]!!)
    secretAccessKey.set(testEnvironment["AWS_SECRET_ACCESS_KEY"]!!)
    buckets.set(listOf(
        "thumbnail-generator-raw-bucket", 
        "thumbnail-generator-thumbnail-bucket"
    ))
    testEnvironmentVariables.set(testEnvironment)
}
