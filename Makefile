# HoldScribe Development Makefile

.PHONY: dev install clean build test help

# Development setup
dev:
	@python3 -m venv dev-env
	@dev-env/bin/pip install -r requirements.txt
	@echo "Development environment ready. Run: source dev-env/bin/activate"

# Install dependencies for development
install:
	@pip install -r requirements.txt

# Build distribution packages  
build:
	@python setup.py sdist bdist_wheel

# Clean build artifacts
clean:
	@rm -rf build/ dist/ *.egg-info/ dev-env/
	@echo "Cleaned build artifacts"

# Test the application
test:
	@python holdscribe.py --help

# Show help
help:
	@echo "HoldScribe Development Commands"
	@echo ""
	@echo "  make dev     - Setup development environment"
	@echo "  make install - Install dependencies" 
	@echo "  make build   - Build distribution packages"
	@echo "  make test    - Test the application"
	@echo "  make clean   - Clean build artifacts"
	@echo ""
	@echo "For usage: brew install ishaq1189/holdscribe/holdscribe"