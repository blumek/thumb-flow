# Makefile for upload_handler Lambda function
.PHONY: help install test lint format build clean docker-build docker-run deploy package venv integration-test localstack-start localstack-stop install-test-deps

# Variables
LAMBDA_NAME = upload_handler
DOCKER_IMAGE = $(LAMBDA_NAME)
DOCKER_TAG = latest
PYTHON = python3
PIP = pip3
PYTEST = pytest
BLACK = black
FLAKE8 = flake8
MYPY = mypy
VENV_DIR = .venv
VENV_BIN = $(VENV_DIR)/bin
VENV_PYTHON = $(VENV_BIN)/python
VENV_PIP = $(VENV_BIN)/pip
LOCALSTACK_CONTAINER = upload-handler-localstack

# AWS/LocalStack Configuration
export AWS_ACCESS_KEY_ID ?= test
export AWS_SECRET_ACCESS_KEY ?= test
export AWS_REGION ?= us-east-1
export AWS_S3_BUCKET_NAME ?= upload-handler-test-bucket
export AWS_ENDPOINT_URL ?= http://localhost:4566

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Virtual environment created. Activate it with: source $(VENV_BIN)/activate"; \
	fi

activate: venv ## Show activation instructions
	@echo "Activate with: source $(VENV_BIN)/activate"

install: venv ## Install dependencies
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "Please activate virtual environment first: source $(VENV_BIN)/activate"; \
		exit 1; \
	fi
	$(PIP) install -e "."

install-dev: venv ## Install development dependencies
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "Please activate virtual environment first: source $(VENV_BIN)/activate"; \
		exit 1; \
	fi
	$(PIP) install -e ".[dev]"

install-test-deps: ## Install dependencies required for tests
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "Please activate virtual environment first: source $(VENV_BIN)/activate"; \
		exit 1; \
	fi
	$(PIP) install pytest pytest-cov pillow boto3 awscli moto

test: ## Run unit tests
	$(PYTEST) test/ -v --cov=src --cov-report=term-missing --ignore=test/integration

integration-test: install-test-deps ## Run integration tests only
	$(PYTEST) test/integration -v

integration-test-setup: install-test-deps ## Setup and run integration tests with LocalStack
	@echo "Setting up environment for integration tests..."
	$(MAKE) localstack-start
	@echo "Waiting for LocalStack to be ready..."
	@sleep 5
	@echo "Creating test bucket..."
	aws --endpoint-url=$(AWS_ENDPOINT_URL) s3 mb s3://$(AWS_S3_BUCKET_NAME) || true
	@echo "Running integration tests..."
	$(MAKE) integration-test
	@echo "Cleaning up..."
	$(MAKE) localstack-stop

localstack-start: ## Start LocalStack in Docker for local testing
	@echo "Starting LocalStack container..."
	@docker run -d --rm --name $(LOCALSTACK_CONTAINER) \
		-p 4566:4566 \
		-e SERVICES=s3 \
		-e DEFAULT_REGION=$(AWS_REGION) \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		localstack/localstack:latest

localstack-stop: ## Stop LocalStack container
	@echo "Stopping LocalStack container..."
	@docker stop $(LOCALSTACK_CONTAINER) || true

test-all: install-test-deps test integration-test ## Run all tests (unit and integration)

lint: ## Run linting checks
	$(FLAKE8) src/ test/ --max-line-length=88 --extend-ignore=E203,W503
	$(MYPY) src/ --ignore-missing-imports

format: ## Format code with black
	$(BLACK) src/ test/ --line-length=88

format-check: ## Check if code is formatted correctly
	$(BLACK) src/ test/ --line-length=88 --check

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf package/
	$(MAKE) localstack-stop

package: clean ## Create deployment package
	$(PYTHON) -m pip install build
	$(PYTHON) -m build
	mkdir -p package
	$(PIP) install dist/*.whl -t package/ --no-deps
	cd package && zip -r ../$(LAMBDA_NAME).zip .

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Run Docker container locally
	docker run --rm -d -p 9000:8080 $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-test: ## Test Docker container with a sample event
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
		-d '{ "image_name": "image", "image_extension": "png", "image_bytes": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" }'
	@echo ""

docker-stop: ## Stop Docker container
	docker ps -q --filter ancestor=$(DOCKER_IMAGE):$(DOCKER_TAG) | xargs -r docker stop

docker-flow: docker-build docker-run docker-test docker-stop ## Full Docker flow

build: format lint test-all package ## Full build pipeline including all tests

check: format-check lint test-all ## Run all checks and tests without making changes

serve: docker-build docker-run ## Build and serve the Lambda function locally
