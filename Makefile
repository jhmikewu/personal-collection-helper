.PHONY: help install dev test run docker-build docker-run clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .

test: ## Run tests
	pytest

run: ## Run the web server
	python -m collection_helper.web

cli: ## Run the CLI
	python -m collection_helper

docker-build: ## Build Docker image
	docker build -t collection-helper .

docker-run: ## Run Docker container
	docker-compose up -d

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-stop: ## Stop Docker containers
	docker-compose down

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf build dist *.egg-info
