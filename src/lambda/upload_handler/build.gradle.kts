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

tasks.register<Exec>("localstackStart") {
    group = "localstack"
    description = "Start LocalStack container for upload-handler"

    commandLine(
        "docker", "run", "-d", "--rm", "--name", "upload-handler-localstack",
        "-p", "4566:4566",
        "-e", "SERVICES=s3",
        "-e", "DEFAULT_REGION=${testEnvironment["AWS_REGION"]}",
        "-e", "AWS_ACCESS_KEY_ID=${testEnvironment["AWS_ACCESS_KEY_ID"]}",
        "-e", "AWS_SECRET_ACCESS_KEY=${testEnvironment["AWS_SECRET_ACCESS_KEY"]}",
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
            } catch (_: Exception) {
                // ignore and retry
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

tasks.register("localstackStop") {
    group = "localstack"
    description = "Stop LocalStack container for upload-handler"

    doLast {
        println("Cleaning up LocalStack for upload-handler...")

        try {
            val stopContainer = ProcessBuilder("docker", "stop", "upload-handler-localstack")
                .start()
            stopContainer.waitFor()
            println("LocalStack container stopped successfully")
        } catch (_: Exception) {
            println("Warning: Failed to stop LocalStack container - it may have already been stopped")
        }

        println("LocalStack cleanup completed for upload-handler")
    }
}

tasks.register<Exec>("createTestBucket") {
    group = "localstack"
    description = "Create test S3 bucket in LocalStack for upload-handler"
    dependsOn("localstackStart")

    commandLine("aws", "--endpoint-url=http://localhost:4566", "s3", "mb", "s3://upload-handler-test-bucket")
    environment(testEnvironment)
    isIgnoreExitValue = true
}

tasks.named<Exec>("runIntegrationTests") {
    environment(testEnvironment)
}

tasks.named("beforeIntegrationTest") {
    dependsOn("localstackStart", "createTestBucket")

    doLast {
        println("LocalStack setup completed for upload-handler integration tests")
    }
}

tasks.named("afterIntegrationTest") {
    dependsOn("localstackStop")

    doLast {
        println("Integration test cleanup completed for upload-handler")
    }
}
