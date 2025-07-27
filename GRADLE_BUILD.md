# ThumbFlow - Gradle Build Guide

This project has been migrated to a multimodule Gradle build system that manages Python Lambda functions.

## Project Structure

```
thumb-flow/
├── build.gradle.kts              # Root build configuration
├── settings.gradle.kts           # Module configuration
├── gradle/                       # Gradle wrapper files
├── src/
│   └── lambda/
│       ├── upload_handler/       # Upload handler Lambda module
│       │   ├── build.gradle.kts  # Module-specific build config
│       │   ├── pyproject.toml    # Python dependencies
│       │   ├── src/              # Python source code
│       │   └── test/             # Python tests
│       └── image_resizer/        # Image resizer Lambda module
│           ├── build.gradle.kts  # Module-specific build config
│           ├── pyproject.toml    # Python dependencies
│           ├── src/              # Python source code (to be implemented)
│           └── test/             # Python tests (to be implemented)
└── terraform/                    # Infrastructure as code
```

## Available Gradle Tasks

### Common Tasks (available for all modules)

#### Development Setup
- `./gradlew createVenv` - Create Python virtual environment
- `./gradlew installDependencies` - Install Python dependencies
- `./gradlew installDevDependencies` - Install development dependencies

#### Testing
- `./gradlew test` - Run unit tests for all modules
- `./gradlew integrationTest` - Run integration tests for all modules
- `./gradlew :upload-handler:test` - Run unit tests for upload-handler only
- `./gradlew :upload-handler:integrationTest` - Run integration tests for upload-handler only
- `./gradlew :upload-handler:testAll` - Run all tests for upload-handler module

#### Code Quality
- `./gradlew lint` - Run linting (flake8 + mypy) for all modules
- `./gradlew format` - Format code with Black for all modules

#### Build & Package
- `./gradlew package` - Package Lambda functions for deployment
- `./gradlew clean` - Clean build artifacts and virtual environments
- `./gradlew dockerBuild` - Build Docker images for Lambda functions

#### LocalStack Integration Testing
- `./gradlew localstackStart` - Start LocalStack container with S3 service
- `./gradlew localstackStop` - Stop LocalStack container
- `./gradlew integrationTestWithLocalStack` - Run integration tests with LocalStack

## Migration from Makefile

The previous Makefile-based build system has been replaced with Gradle. Here's the command mapping:

| Old Makefile Command | New Gradle Command |
|---------------------|-------------------|
| `make install` | `./gradlew installDependencies` |
| `make install-dev` | `./gradlew installDevDependencies` |
| `make test` | `./gradlew test` |
| `make integration-test` | `./gradlew integrationTest` |
| `make lint` | `./gradlew lint` |
| `make format` | `./gradlew format` |
| `make clean` | `./gradlew clean` |
| `make docker-build` | `./gradlew dockerBuild` |
| `make package` | `./gradlew package` |
| `make localstack-start` | `./gradlew localstackStart` |
| `make localstack-stop` | `./gradlew localstackStop` |
| `make integration-test-setup` | `./gradlew integrationTestWithLocalStack` |

## Getting Started

1. **Initialize the project:**
   ```bash
   ./gradlew installDevDependencies
   ```

2. **Run tests:**
   ```bash
   ./gradlew test
   ```

3. **Run integration tests with LocalStack:**
   ```bash
   ./gradlew integrationTestWithLocalStack
   ```

4. **Format and lint code:**
   ```bash
   ./gradlew format lint
   ```

5. **Package for deployment:**
   ```bash
   ./gradlew package
   ```

## Environment Variables

The build system automatically sets up the following environment variables for testing:

- `AWS_ACCESS_KEY_ID=test`
- `AWS_SECRET_ACCESS_KEY=test`
- `AWS_REGION=us-east-1`
- `AWS_S3_BUCKET_NAME=upload-handler-test-bucket`
- `AWS_ENDPOINT_URL=http://localhost:4566`

## Module-Specific Configuration

Each Lambda module (`upload-handler`, `image-resizer`) has its own:
- `build.gradle.kts` - Module-specific Gradle configuration
- `pyproject.toml` - Python dependencies and tool configuration
- Independent virtual environments and test suites

## Benefits of Gradle Migration

1. **Unified Build System** - Single tool for all build operations
2. **Parallel Execution** - Gradle can run tasks in parallel
3. **Dependency Management** - Better handling of module dependencies
4. **IDE Integration** - Better support in IDEs like IntelliJ IDEA
5. **Incremental Builds** - Only rebuild what's changed
6. **Cross-Platform** - Works consistently across different operating systems
7. **Extensible** - Easy to add new modules and customize build logic
