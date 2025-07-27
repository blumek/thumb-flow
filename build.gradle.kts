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

    tasks.register<Exec>("createVenv") {
        group = "python"
        description = "Create Python virtual environment"

        commandLine("python3", "-m", "venv", ".venv")
        workingDir = projectDir
    }

    tasks.register<Exec>("installDependencies") {
        group = "python"
        description = "Install Python dependencies"
        dependsOn("createVenv")

        commandLine(".venv/bin/pip", "install", "-e", ".")
        workingDir = projectDir
    }

    tasks.register<Exec>("installDevDependencies") {
        group = "python"
        description = "Install Python development dependencies"
        dependsOn("createVenv")

        commandLine(".venv/bin/pip", "install", "-e", ".[dev]")
        workingDir = projectDir
    }

    tasks.register<Exec>("test") {
        group = "verification"
        description = "Run unit tests for ${project.name}"
        dependsOn("installDevDependencies")

        commandLine(
            ".venv/bin/pytest",
            "test/",
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
            "--ignore=test/integration"
        )
        workingDir = projectDir
    }

    tasks.register<Exec>("integrationTest") {
        group = "verification"
        description = "Run integration tests for ${project.name}"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/pytest", "test/integration", "-v")
        workingDir = projectDir
    }

    tasks.register<Exec>("lint") {
        group = "verification"
        description = "Run linting checks"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/flake8", "src/", "test/", "--max-line-length=88", "--extend-ignore=E203,W503")
        workingDir = projectDir
    }

    tasks.register<Exec>("formatCheck") {
        group = "verification"
        description = "Check code formatting with Black"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/black", "--check", "src/", "test/")
        workingDir = projectDir
    }

    tasks.register<Exec>("typeCheck") {
        group = "verification"
        description = "Run type checking with mypy"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/mypy", "src/", "--ignore-missing-imports")
        workingDir = projectDir
    }

    tasks.register<Exec>("securityCheck") {
        group = "verification"
        description = "Run security checks with bandit"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/bandit", "-r", "src/", "-ll")
        workingDir = projectDir
    }

    tasks.register<Exec>("format") {
        group = "formatting"
        description = "Format code with Black"
        dependsOn("installDevDependencies")

        commandLine(".venv/bin/black", "src/", "test/")
        workingDir = projectDir
    }

    tasks.register("clean") {
        group = "build"
        description = "Clean build artifacts"

        doLast {
            delete(".venv")
            delete("build")
            delete("dist")
            delete(fileTree(projectDir) {
                include("**/__pycache__/**")
                include("**/*.pyc")
                include("**/*.pyo")
                include("**/*.egg-info/**")
            })
        }
    }

    tasks.register<Exec>("dockerBuild") {
        group = "docker"
        description = "Build Docker image"

        commandLine("docker", "build", "-t", "${project.name}:latest", ".")
        workingDir = projectDir
    }
}
