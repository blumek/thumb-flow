import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.api.tasks.Exec
import org.gradle.kotlin.dsl.*

class LocalStackPlugin : Plugin<Project> {
    override fun apply(project: Project) {
        with(project) {
            val localStackExtension = extensions.create<LocalStackExtension>("localStack")

            afterEvaluate {
                val projectName = project.name

                configureTasks(localStackExtension.toConfigureTasksRequest(projectName))
                configureIntegrationTests(localStackExtension, projectName)
            }
        }
    }

    private fun LocalStackExtension.toConfigureTasksRequest(projectName: String): ConfigureTasksRequest {
        return ConfigureTasksRequest(
            containerName = containerName.get(),
            port = port.get(),
            services = services.get(),
            region = region.get(),
            accessKey = accessKeyId.get(),
            secretKey = secretAccessKey.get(),
            extension = this,
            projectName = projectName
        )
    }

    private fun Project.configureTasks(request: ConfigureTasksRequest) {
        tasks.register<Exec>("localstackStart") {
            group = "localstack"
            description = "Start LocalStack container for ${request.projectName}"

            commandLine(
                "docker", "run", "-d", "--rm", "--name", request.containerName,
                "-p", "${request.port}:4566",
                "-e", "SERVICES=${request.services}",
                "-e", "DEFAULT_REGION=${request.region}",
                "-e", "AWS_ACCESS_KEY_ID=${request.accessKey}",
                "-e", "AWS_SECRET_ACCESS_KEY=${request.secretKey}",
                "localstack/localstack:latest"
            )

            doLast {
                println("LocalStack container started for ${request.projectName}. Waiting for services to be ready...")

                val endpoint = "http://localhost:${request.port}"
                waitForLocalStackReady(endpoint)
            }
        }

        tasks.register("localstackStop") {
            group = "localstack"
            description = "Stop LocalStack container for ${request.projectName}"

            val taskContainerName = request.containerName

            doLast {
                println("Cleaning up LocalStack for ${request.projectName}...")

                try {
                    val stopContainer = ProcessBuilder("docker", "stop", taskContainerName)
                        .start()
                    stopContainer.waitFor()
                    println("LocalStack container stopped successfully")
                } catch (_: Exception) {
                    println("Warning: Failed to stop LocalStack container - it may have already been stopped")
                }

                println("LocalStack cleanup completed for ${request.projectName}")
            }
        }

        request.extension.buckets.get().forEach { bucket ->
            tasks.register<Exec>("create${bucket.capitalizeFirstChar()}Bucket") {
                group = "localstack"
                description = "Create $bucket S3 bucket in LocalStack for ${request.projectName}"
                dependsOn("localstackStart")

                val endpoint = "http://localhost:${request.port}"
                commandLine("aws", "--endpoint-url=$endpoint", "s3", "mb", "s3://$bucket")

                val testEnv = request.extension.testEnvironmentVariables.get()
                if (testEnv.isNotEmpty()) {
                    environment(testEnv)
                }

                isIgnoreExitValue = true
            }
        }
    }

    private fun Project.configureIntegrationTests(extension: LocalStackExtension, projectName: String) {
        if (tasks.names.contains("beforeIntegrationTest")) {
            val dependencyTasks = mutableListOf("localstackStart")

            extension.buckets.get().forEach { bucket ->
                dependencyTasks.add("create${bucket.capitalizeFirstChar()}Bucket")
            }

            tasks.named("beforeIntegrationTest") {
                dependsOn(*dependencyTasks.toTypedArray())

                doLast {
                    println("LocalStack setup completed for $projectName integration tests")
                }
            }
        }

        if (tasks.names.contains("afterIntegrationTest")) {
            tasks.named("afterIntegrationTest") {
                dependsOn("localstackStop")

                doLast {
                    println("Integration test cleanup completed for $projectName")
                }
            }
        }

        if (tasks.names.contains("runIntegrationTests")) {
            tasks.named<Exec>("runIntegrationTests") {
                val testEnv = extension.testEnvironmentVariables.get()
                if (testEnv.isNotEmpty()) {
                    environment(testEnv)
                }
            }
        }
    }

    private fun waitForLocalStackReady(endpoint: String) {
        var attempts = 0
        val maxAttempts = 30
        while (attempts < maxAttempts) {
            try {
                val healthCheck =
                    ProcessBuilder("curl", "-s", "$endpoint/_localstack/health")
                        .start()
                healthCheck.waitFor()
                if (healthCheck.exitValue() == 0) {
                    println("LocalStack is ready!")
                    Thread.sleep(2000)
                    return
                }
            } catch (_: Exception) {
                // Ignore exceptions, will retry
            }
            attempts++
            Thread.sleep(1000)
            println("Waiting for LocalStack... (attempt $attempts/$maxAttempts)")
        }

        throw RuntimeException("LocalStack failed to start within expected time")
    }

    private fun String.capitalizeFirstChar(): String {
        if (isEmpty()) return this
        return this[0].uppercaseChar() + substring(1)
    }
}

data class ConfigureTasksRequest(
    val containerName: String,
    val port: Int,
    val services: String,
    val region: String,
    val accessKey: String,
    val secretKey: String,
    val extension: LocalStackExtension,
    val projectName: String
)