plugins {
    id("com.github.psxpaul.execfork")
    id("com.blumek.thumbflow.localstack")
}

description = "AWS Lambda function for handling image uploads"

val testEnvironment = mapOf(
    "AWS_ACCESS_KEY_ID" to "test",
    "AWS_SECRET_ACCESS_KEY" to "test",
    "AWS_REGION" to "us-east-1",
    "AWS_S3_BUCKET_NAME" to "upload-handler-test-bucket",
    "AWS_ENDPOINT_URL" to "http://localhost:4566",
    "AWS_SQS_QUEUE_URL" to "http://localhost:4566/000000000000/upload-handler-test-queue",
)

localStack {
    containerName.set("upload-handler-localstack")
    port.set(4566)
    services.set("s3")
    region.set(testEnvironment["AWS_REGION"]!!)
    accessKeyId.set(testEnvironment["AWS_ACCESS_KEY_ID"]!!)
    secretAccessKey.set(testEnvironment["AWS_SECRET_ACCESS_KEY"]!!)
    buckets.set(listOf("upload-handler-test-bucket"))
    testEnvironmentVariables.set(testEnvironment)
}
