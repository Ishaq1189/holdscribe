# HoldScribe Makefile
# Push-to-talk voice transcription with AI

.PHONY: run start install setup clean test help

# Default target - run with right Alt key
run:
	@python holdscribe.py --key alt_r

# Alternative target names
start: run

# Run with different keys
run-space:
	@python holdscribe.py --key space

run-f8:
	@python holdscribe.py --key f8

run-f9:
	@python holdscribe.py --key f9

# Run with different AI models
run-tiny:
	@python holdscribe.py --key alt_r --model tiny

run-small:
	@python holdscribe.py --key alt_r --model small

run-medium:
	@python holdscribe.py --key alt_r --model medium

run-large:
	@python holdscribe.py --key alt_r --model large

# Install dependencies
install:
	@pip install -r requirements.txt

# Setup virtual environment and install dependencies
setup:
	@python3 -m venv holdscribe-env
	@source holdscribe-env/bin/activate && pip install -r requirements.txt
	@echo "Setup complete! Run 'source holdscribe-env/bin/activate && make run' to start."

# Build distribution
build:
	@python setup.py sdist bdist_wheel

# Clean build artifacts
clean:
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf holdscribe-env/
	@echo "Cleaned build artifacts and virtual environment."

# Test the application
test:
	@python holdscribe.py --help

# Show help
help:
	@echo "HoldScribe - Push-to-talk voice transcription"
	@echo ""
	@echo "Usage:"
	@echo "  make run        - Start with right Alt key (default)"
	@echo "  make run-space  - Start with space bar"
	@echo "  make run-f8     - Start with F8 key"
	@echo "  make run-f9     - Start with F9 key"
	@echo ""
	@echo "Models:"
	@echo "  make run-tiny   - Use tiny AI model (fastest)"
	@echo "  make run-small  - Use small AI model"
	@echo "  make run-medium - Use medium AI model"
	@echo "  make run-large  - Use large AI model (most accurate)"
	@echo ""
	@echo "Development:"
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make install    - Install dependencies"
	@echo "  make build      - Build distribution packages"
	@echo "  make test       - Test the application"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make help       - Show this help"