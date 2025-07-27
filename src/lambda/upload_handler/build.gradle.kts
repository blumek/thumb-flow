plugins {
    id("com.github.psxpaul.execfork")
}

description = "AWS Lambda function for handling image uploads"

val testEnvironment = mapOf(
    "AWS_ACCESS_KEY_ID" to "test",
    "AWS_SECRET_ACCESS_KEY" to "test",
    "AWS_REGION" to "us-east-1",
    "AWS_S3_BUCKET_NAME" to "upload-handler-test-bucket",
    "AWS_ENDPOINT_URL" to "http://localhost:4566"
)

tasks.named<Exec>("integrationTest") {
    environment(testEnvironment)
}

tasks.register<Exec>("localstackStart") {
    group = "localstack"
    description = "Start LocalStack container for upload-handler"

    commandLine(
        "docker", "run", "-d", "--rm", "--name", "upload-handler-localstack",
        "-p", "4566:4566",
        "-e", "SERVICES=s3",
        "-e", "DEFAULT_REGION=us-east-1",
        "-e", "AWS_ACCESS_KEY_ID=test",
        "-e", "AWS_SECRET_ACCESS_KEY=test",
        "localstack/localstack:latest"
    )

    doLast {
        println("LocalStack container started for upload-handler. Waiting for services to be ready...")

        var attempts = 0
        val maxAttempts = 30
        while (attempts < maxAttempts) {
            try {
                val healthCheck = ProcessBuilder("curl", "-s", "http://localhost:4566/_localstack/health")
                    .start()
                healthCheck.waitFor()
                if (healthCheck.exitValue() == 0) {
                    println("LocalStack is ready for upload-handler!")
                    Thread.sleep(2000)
                    break
                }
            } catch (e: Exception) {
                // Ignore and retry
            }
            attempts++
            Thread.sleep(1000)
            println("Waiting for LocalStack upload-handler... (attempt $attempts/$maxAttempts)")
        }

        if (attempts >= maxAttempts) {
            throw RuntimeException("LocalStack failed to start within expected time for upload-handler")
        }
    }
}

tasks.register<Exec>("localstackStop") {
    group = "localstack"
    description = "Stop LocalStack container for upload-handler"

    commandLine("docker", "stop", "upload-handler-localstack")
    isIgnoreExitValue = true
}

tasks.register<Exec>("createTestBucket") {
    group = "localstack"
    description = "Create test S3 bucket in LocalStack for upload-handler"
    dependsOn("localstackStart")

    commandLine("aws", "--endpoint-url=http://localhost:4566", "s3", "mb", "s3://upload-handler-test-bucket")
    environment("AWS_ACCESS_KEY_ID", "test")
    environment("AWS_SECRET_ACCESS_KEY", "test")
    environment("AWS_REGION", "us-east-1")
    isIgnoreExitValue = true
}

tasks.register<Exec>("integrationTestWithLocalStack") {
    group = "verification"
    description = "Run integration tests with LocalStack for upload-handler"
    dependsOn("createTestBucket", "installDevDependencies")
    finalizedBy("localstackStop")

    commandLine(
        ".venv/bin/pytest",
        "test/integration",
        "-v",
        "--tb=short"
    )
    workingDir = projectDir

    environment("AWS_ACCESS_KEY_ID", "test")
    environment("AWS_SECRET_ACCESS_KEY", "test")
    environment("AWS_REGION", "us-east-1")
    environment("AWS_ENDPOINT_URL", "http://localhost:4566")
    environment("LOCALSTACK_ENDPOINT", "http://localhost:4566")
    environment("AWS_S3_BUCKET_NAME", "upload-handler-test-bucket")
}
