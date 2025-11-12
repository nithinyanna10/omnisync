.PHONY: help setup start stop test clean

help:
	@echo "OmniSync Makefile Commands:"
	@echo "  make setup     - Install dependencies"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean up generated files"

setup:
	@echo "Setting up OmniSync..."
	@cd sdk/python && pip install -r requirements.txt && pip install -e .
	@cd hub/frontend && npm install
	@echo "Setup complete!"

start:
	@echo "Starting OmniSync services..."
	docker-compose up -d
	@echo "Services started! Hub UI: http://localhost:3001"

stop:
	@echo "Stopping OmniSync services..."
	docker-compose down
	@echo "Services stopped!"

test:
	@echo "Running tests..."
	cd sdk/python && pytest tests/

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@echo "Clean complete!"

