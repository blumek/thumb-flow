plugins {
    id("com.github.psxpaul.execfork") version "0.2.2" apply false
}

allprojects {
    group = "com.blumek.thumbflow"
    version = "0.1.0"
}

subprojects {
    apply(plugin = "com.github.psxpaul.execfork")

    repositories {
        mavenCentral()
    }

    val currentProjectDir = projectDir
    val currentProjectName = project.name

    tasks.register<Exec>("createVenv") {
        group = "python"
        description = "Create Python virtual environment"

        commandLine("python3", "-m", "venv", ".venv")
        workingDir = currentProjectDir
    }

    tasks.register<Exec>("installDependencies") {
        group = "python"
        description = "Install Python dependencies"
        dependsOn("createVenv")

        commandLine(".venv/bin/pip", "install", "-e", ".")
        workingDir = currentProjectDir
    }

    tasks.register<Exec>("installDevDependencies") {
        group = "python"
        description = "Install Python development dependencies"
        dependsOn("createVenv")

        commandLine(".venv/bin/pip", "install", "-e", ".[dev]")
        workingDir = currentProjectDir
    }

    tasks.register<Exec>("test") {
        group = "verification"
        description = "Run unit tests for $currentProjectName"
        dependsOn("installDevDependencies")

        val testReportsDir = layout.buildDirectory.dir("reports/tests")
        val coverageReportsDir = layout.buildDirectory.dir("reports/coverage")

        doFirst {
            coverageReportsDir.get().asFile.mkdirs()
        }

        commandLine(
            ".venv/bin/pytest",
            "test/",
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=xml",
            "--junit-xml=${testReportsDir.get().asFile}/junit.xml",
            "--ignore=test/integration"
        )
        workingDir = currentProjectDir
    }

    tasks.register("beforeIntegrationTest") {
        group = "verification"
        description = "Hook executed before integration tests"
    }

    tasks.register("afterIntegrationTest") {
        group = "verification"
        description = "Hook executed after integration tests"
    }

    tasks.register<Exec>("runIntegrationTests") {
        group = "verification"
        description = "Execute the actual integration tests"
        dependsOn("installDevDependencies")

        val testReportsDir = layout.buildDirectory.dir("reports/tests")

        commandLine(
            ".venv/bin/pytest",
            "test/integration",
            "-v",
            "--junit-xml=${testReportsDir.get().asFile}/integration-junit.xml"
        )
        workingDir = currentProjectDir
    }

    tasks.register("integrationTest") {
        group = "verification"
        description = "Run integration tests for $currentProjectName with template pattern"
        dependsOn("beforeIntegrationTest", "runIntegrationTests")
        finalizedBy("afterIntegrationTest")
    }

    tasks.named("runIntegrationTests") {
        mustRunAfter("beforeIntegrationTest")
    }

    tasks.named("afterIntegrationTest") {
        mustRunAfter("runIntegrationTests")
    }

    tasks.register<Exec>("lint") {
        group = "verification"
        description = "Run linting checks"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/flake8", "src/", "test/", "--max-line-length=88", "--extend-ignore=E203,W503")
        workingDir = currentProjectDir
    }

    tasks.register<Exec>("formatCheck") {
        group = "verification"
        description = "Check code formatting with Black"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/black", "--check", "src/", "test/")
        workingDir = currentProjectDir
    }

    tasks.register<Exec>("typeCheck") {
        group = "verification"
        description = "Run type checking with mypy"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/mypy", "src/", "--ignore-missing-imports")
        workingDir = currentProjectDir
    }

    tasks.register<Exec>("securityCheck") {
        group = "verification"
        description = "Run security checks with bandit"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/bandit", "-r", "src/", "-ll")
        workingDir = currentProjectDir
    }

    tasks.register<Exec>("format") {
        group = "formatting"
        description = "Format code with Black"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/black", "src/", "test/")
        workingDir = currentProjectDir
    }

    tasks.register("clean") {
        group = "build"
        description = "Clean all build artifacts, caches, and generated files"

        doLast {
            logger.info("Cleaning project: $currentProjectName")

            delete(".venv")
            delete("build")
            delete(fileTree(currentProjectDir) {
                include("**/__pycache__/**")
                include("**/*.pyc")
                include("**/*.pyo")
                include("**/*.pyd")
                include("**/*.egg-info/**")
                include("**/.eggs/**")
                include("**/.coverage")
                include("**/.coverage.*")
                include("**/htmlcov/**")
                include("**/.pytest_cache/**")
                include("**/.mypy_cache/**")
                include("**/*.tmp")
                include("**/*.temp")
                include("**/*~")
            })

            logger.info("Cleaned project: $currentProjectName")
        }
    }

    tasks.register<Exec>("dockerBuild") {
        group = "docker"
        description = "Build Docker image"

        commandLine("docker", "build", "-t", "$currentProjectName:latest", ".")
        workingDir = currentProjectDir
    }
}
