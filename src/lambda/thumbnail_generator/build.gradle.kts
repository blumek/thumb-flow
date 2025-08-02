plugins {
    id("com.github.psxpaul.execfork")
}

description = "AWS Lambda function for image resizing and thumbnail generation"

val testEnvironment = mapOf(
    "AWS_ACCESS_KEY_ID" to "test",
    "AWS_SECRET_ACCESS_KEY" to "test",
    "AWS_REGION" to "us-east-1",
    "AWS_S3_RAW_BUCKET_NAME" to "thumbnail-generator-raw-bucket", // Zmieniona nazwa bucketa dla oryginalnych obrazów
    "AWS_S3_THUMBNAIL_BUCKET_NAME" to "thumbnail-generator-thumbnail-bucket", // Zmieniona nazwa bucketa dla miniatur
    "AWS_ENDPOINT_URL" to "http://localhost:4567"
)

tasks.register<Exec>("localstackStart") {
    group = "localstack"
    description = "Start LocalStack container for thumbnail-generator"

    commandLine(
        "docker", "run", "-d", "--rm", "--name", "thumbnail-generator-localstack",
        "-p", "4567:4566",
        "-e", "SERVICES=s3",
        "-e", "DEFAULT_REGION=${testEnvironment["AWS_REGION"]}",
        "-e", "AWS_ACCESS_KEY_ID=${testEnvironment["AWS_ACCESS_KEY_ID"]}",
        "-e", "AWS_SECRET_ACCESS_KEY=${testEnvironment["AWS_SECRET_ACCESS_KEY"]}",
        "localstack/localstack:latest"
    )

    doLast {
        println("LocalStack container started for thumbnail-generator. Waiting for services to be ready...")

        var attempts = 0
        val maxAttempts = 30
        while (attempts < maxAttempts) {
            try {
                val healthCheck = ProcessBuilder("curl", "-s", "http://localhost:4567/_localstack/health")  // Zmieniony port na 4567
                    .start()
                healthCheck.waitFor()
                if (healthCheck.exitValue() == 0) {
                    println("LocalStack is ready for thumbnail-generator!")
                    Thread.sleep(2000)
                    break
                }
            } catch (_: Exception) {
                // ignore and retry
            }
            attempts++
            Thread.sleep(1000)
            println("Waiting for LocalStack thumbnail-generator... (attempt $attempts/$maxAttempts)")
        }

        if (attempts >= maxAttempts) {
            throw RuntimeException("LocalStack failed to start within expected time for thumbnail-generator")
        }
    }
}

tasks.register("localstackStop") {
    group = "localstack"
    description = "Stop LocalStack container for thumbnail-generator"

    doLast {
        println("Cleaning up LocalStack for thumbnail-generator...")

        try {
            val stopContainer = ProcessBuilder("docker", "stop", "thumbnail-generator-localstack")
                .start()
            stopContainer.waitFor()
            println("LocalStack container stopped successfully")
        } catch (_: Exception) {
            println("Warning: Failed to stop LocalStack container - it may have already been stopped")
        }

        println("LocalStack cleanup completed for thumbnail-generator")
    }
}

tasks.register<Exec>("createRawBucket") {
    group = "localstack"
    description = "Create raw images S3 bucket in LocalStack for thumbnail-generator"
    dependsOn("localstackStart")

    commandLine("aws", "--endpoint-url=http://localhost:4567", "s3", "mb", "s3://${testEnvironment["AWS_S3_RAW_BUCKET_NAME"]}")
    environment(testEnvironment)
    isIgnoreExitValue = true
}

tasks.register<Exec>("createThumbnailBucket") {
    group = "localstack"
    description = "Create thumbnails S3 bucket in LocalStack for thumbnail-generator"
    dependsOn("localstackStart")

    commandLine("aws", "--endpoint-url=http://localhost:4567", "s3", "mb", "s3://${testEnvironment["AWS_S3_THUMBNAIL_BUCKET_NAME"]}")
    environment(testEnvironment)
    isIgnoreExitValue = true
}

tasks.named<Exec>("runIntegrationTests") {
    environment(testEnvironment)
}

tasks.named("beforeIntegrationTest") {
    dependsOn("localstackStart", "createRawBucket", "createThumbnailBucket") // Dodane zadanie createThumbnailBucket

    doLast {
        println("LocalStack setup completed for thumbnail-generator integration tests")
    }
}

tasks.named("afterIntegrationTest") {
    dependsOn("localstackStop")

    doLast {
        println("Integration test cleanup completed for thumbnail-generator")
    }
}
