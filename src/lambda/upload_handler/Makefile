# Makefile for upload_handler Lambda function
.PHONY: help install test lint format build clean docker-build docker-run deploy package venv

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

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Virtual environment created. Activate it with: source $(VENV_BIN)/activate";

activate: venv ## Show activation instructions
	@echo "Activate with: source $(VENV_BIN)/activate"

install: venv ## Install dependencies
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "Please activate virtual environment first: source $(VENV_BIN)/activate"; \
		exit 1; \
	fi
	$(PIP) install -r requirements.txt

install-dev: venv ## Install development dependencies
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "Please activate virtual environment first: source $(VENV_BIN)/activate"; \
		exit 1; \
	fi
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov black flake8 mypy boto3-stubs[essential]

test: ## Run tests
	$(PYTEST) test/ -v --cov=src --cov-report=term-missing

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

package: clean ## Create deployment package
	mkdir -p package
	$(PIP) install -r requirements.txt -t package/
	cp -r src/* package/
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

build: format lint test package ## Full build pipeline

check: format-check lint test ## Run all checks without making changes

serve: docker-build docker-run ## Build and serve the Lambda function locally