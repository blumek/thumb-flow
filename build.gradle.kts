plugins {
    alias(libs.plugins.execfork) apply false
}

allprojects {
    group = "com.blumek.thumbflow"
    version = "0.1.0"

    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "com.github.psxpaul.execfork")

    val projectName = name
    val isWindows = System.getProperty("os.name").lowercase().contains("windows")
    val pythonExecutable = if (isWindows) "python" else "python3"
    val venvBinDir = if (isWindows) ".venv/Scripts" else ".venv/bin"
    val pipExecutable = "$venvBinDir/pip"
    val pytestExecutable = "$venvBinDir/pytest"
    val blackExecutable = "$venvBinDir/black"
    val flake8Executable = "$venvBinDir/flake8"
    val mypyExecutable = "$venvBinDir/mypy"
    val banditExecutable = "$venvBinDir/bandit"

    tasks.withType<Exec> {
        outputs.upToDateWhen { false }
    }

    tasks.register<Exec>("createVenv") {
        group = "python"
        description = "Create Python virtual environment"

        inputs.file("pyproject.toml").optional()
        outputs.dir(".venv")

        doFirst {
            if (File(".venv").exists()) {
                throw StopExecutionException("Virtual environment already exists")
            }
        }

        commandLine(pythonExecutable, "-m", "venv", ".venv")
    }

    tasks.register<Exec>("installDependencies") {
        group = "python"
        description = "Install Python dependencies"
        dependsOn("createVenv")

        inputs.file("pyproject.toml")
        outputs.dir("$venvBinDir/../lib")

        commandLine(pipExecutable, "install", "-e", ".")
    }

    tasks.register<Exec>("installDevDependencies") {
        group = "python"
        description = "Install Python development dependencies"
        dependsOn("createVenv")

        inputs.file("pyproject.toml")
        outputs.dir("$venvBinDir/../lib")

        commandLine(pipExecutable, "install", "-e", ".[dev]")
    }

    tasks.register<Exec>("test") {
        group = "verification"
        description = "Run unit tests for $projectName"
        dependsOn("installDevDependencies")

        inputs.dir("src")
        inputs.files(fileTree("test") {
            exclude("integration/**")
        })
        inputs.file("pyproject.toml")

        val testReportsDir = layout.buildDirectory.dir("reports/tests")
        val coverageReportsDir = layout.buildDirectory.dir("reports/coverage")

        outputs.dir(testReportsDir)
        outputs.dir(coverageReportsDir)

        doFirst {
            testReportsDir.get().asFile.mkdirs()
            coverageReportsDir.get().asFile.mkdirs()
        }

        commandLine(
            pytestExecutable,
            "test/",
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:${coverageReportsDir.get().asFile}/html",
            "--cov-report=xml:${coverageReportsDir.get().asFile}/coverage.xml",
            "--junit-xml=${testReportsDir.get().asFile}/junit.xml",
            "--ignore=test/integration"
        )
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
            pytestExecutable,
            "test/integration",
            "-v",
            "--junit-xml=${testReportsDir.get().asFile}/integration-junit.xml"
        )
    }

    tasks.register("integrationTest") {
        group = "verification"
        description = "Run integration tests for $projectName"
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

        inputs.dir("src")
        inputs.dir("test")
        inputs.file("pyproject.toml")
        outputs.upToDateWhen { false }

        commandLine(flake8Executable, "src/", "test/", "--max-line-length=88", "--extend-ignore=E203,W503")
    }

    tasks.register<Exec>("formatCheck") {
        group = "verification"
        description = "Check code formatting with Black"
        dependsOn("installDevDependencies")

        inputs.dir("src")
        inputs.dir("test")
        inputs.file("pyproject.toml")
        outputs.upToDateWhen { false }

        commandLine(blackExecutable, "--check", "src/", "test/")
    }

    tasks.register<Exec>("typeCheck") {
        group = "verification"
        description = "Run type checking with mypy"
        dependsOn("installDevDependencies")

        inputs.dir("src")
        inputs.file("pyproject.toml")
        outputs.upToDateWhen { false }

        commandLine(mypyExecutable, "src/", "--ignore-missing-imports")
    }

    tasks.register<Exec>("securityCheck") {
        group = "verification"
        description = "Run security checks with bandit"
        dependsOn("installDevDependencies")

        inputs.dir("src")
        outputs.upToDateWhen { false }

        commandLine(banditExecutable, "-r", "src/", "-ll")
    }

    tasks.register("check") {
        group = "verification"
        description = "Run all verification tasks"
        dependsOn("lint", "formatCheck", "typeCheck", "securityCheck", "test")
    }

    tasks.register("quickCheck") {
        group = "verification"
        description = "Run quick verification tasks (no tests)"
        dependsOn("lint", "formatCheck", "typeCheck")
    }

    tasks.register<Exec>("format") {
        group = "formatting"
        description = "Format code with Black"
        dependsOn("installDevDependencies")

        inputs.dir("src")
        inputs.dir("test")
        outputs.upToDateWhen { false }

        commandLine(blackExecutable, "src/", "test/")
    }

    tasks.register<Delete>("clean") {
        group = "build"
        description = "Clean all build artifacts, caches, and generated files"

        delete(".venv", "build")
        delete(fileTree(".") {
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

        doLast {
            println("Cleaned project: $projectName")
        }
    }

    tasks.register<Exec>("dockerBuild") {
        group = "docker"
        description = "Build Docker image"

        commandLine("docker", "build", "-t", "blumek/$projectName:latest", ".")
    }
}
