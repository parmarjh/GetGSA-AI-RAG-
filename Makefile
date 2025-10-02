# GetGSA Makefile

.PHONY: install test run clean lint format

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python run_tests.py

# Run the application
run:
	streamlit run app.py

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .pytest_cache
	rm -rf .coverage

# Lint code
lint:
	flake8 backend/ tests/ --max-line-length=100 --ignore=E203,W503

# Format code
format:
	black backend/ tests/ --line-length=100

# Run all checks
check: lint test

# Development setup
dev-setup: install
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the Streamlit app"
	@echo "Run 'make test' to run tests"

# Production build
build: clean
	@echo "Building for production..."
	@echo "Streamlit: Application ready"
	@echo "Tests: Test suite ready"

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install Python dependencies"
	@echo "  test         - Run test suite"
	@echo "  run          - Start Streamlit app"
	@echo "  clean        - Clean up temporary files"
	@echo "  lint         - Run code linter"
	@echo "  format       - Format code with black"
	@echo "  check        - Run linting and tests"
	@echo "  dev-setup    - Set up development environment"
	@echo "  build        - Build for production"
	@echo "  help         - Show this help message"
