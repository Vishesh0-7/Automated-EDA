# Automated EDA Tool - Makefile
# Provides common tasks and shortcuts

.PHONY: help install test clean example run setup lint format

# Default target
help:
	@echo "🔍 Automated EDA Tool - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup          Setup Python environment and install dependencies"
	@echo "  make install        Install/update dependencies"
	@echo ""
	@echo "Usage Commands:"
	@echo "  make example        Run example analysis"
	@echo "  make run FILE=<csv>  Run EDA on specified file"
	@echo "  make test           Run tests and validation"
	@echo ""
	@echo "Development Commands:"
	@echo "  make lint           Check code quality"
	@echo "  make format         Format code"
	@echo "  make clean          Clean up generated files"
	@echo ""
	@echo "Examples:"
	@echo "  make run FILE=data/loan_approval.csv"
	@echo "  make run FILE=data/my_dataset.csv OUTPUT=my_analysis"
	@echo ""

# Setup Python environment
setup:
	@echo "🔧 Setting up Python environment..."
	python3 -m venv .venv
	@echo "📦 Installing dependencies..."
	.venv/bin/pip install -r requirements.txt
	@echo "✅ Setup complete!"

# Install dependencies
install:
	@echo "📦 Installing/updating dependencies..."
	.venv/bin/pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Run example analysis
example:
	@echo "🚀 Running example analysis..."
	.venv/bin/python example_usage.py

# Run EDA on specified file
run:
ifndef FILE
	@echo "❌ Error: Please specify FILE=<csv_file>"
	@echo "Example: make run FILE=data/loan_approval.csv"
	@exit 1
endif
	@echo "🔍 Running EDA on: $(FILE)"
ifdef OUTPUT
	.venv/bin/python automated_eda.py --file $(FILE) --output-dir $(OUTPUT)
else
	.venv/bin/python automated_eda.py --file $(FILE)
endif

# Run tests and validation
test:
	@echo "🧪 Running tests..."
	@echo "📊 Testing with sample data..."
	.venv/bin/python automated_eda.py --file data/loan_approval.csv --output-dir test_output --no-profiling
	@echo "✅ Basic test completed!"
	
	@echo "🔧 Testing API usage..."
	.venv/bin/python -c "from src.main_eda import AutomatedEDA; print('✅ Import test passed')"
	@echo "✅ All tests passed!"

# Code quality check
lint:
	@echo "🔍 Checking code quality..."
	@if command -v flake8 >/dev/null 2>&1; then \
		.venv/bin/flake8 src/ --max-line-length=100 --ignore=E501,W503; \
	else \
		echo "⚠️  flake8 not installed, skipping lint check"; \
	fi

# Format code
format:
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		.venv/bin/black src/ --line-length=100; \
	else \
		echo "⚠️  black not installed, skipping formatting"; \
	fi

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf eda_output/
	rm -rf example_output/
	rm -rf api_example_output/
	rm -rf test_output/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "✅ Cleanup complete!"

# Development setup
dev-setup: setup
	@echo "🛠️  Installing development dependencies..."
	.venv/bin/pip install flake8 black pytest
	@echo "✅ Development environment ready!"

# Quick start
quickstart: setup example
	@echo "🎉 Quick start complete!"
	@echo "💡 Try: make run FILE=data/loan_approval.csv"

# Show project status
status:
	@echo "📊 Project Status"
	@echo "================"
	@echo "Python Environment: $$(if [ -d .venv ]; then echo '✅ Active'; else echo '❌ Not setup'; fi)"
	@echo "Sample Data: $$(if [ -f data/loan_approval.csv ]; then echo '✅ Available'; else echo '❌ Missing'; fi)"
	@echo "Last Analysis: $$(if [ -d eda_output ]; then echo '✅ Found in eda_output/'; else echo '❌ None found'; fi)"
	@echo ""
	@echo "Files:"
	@ls -la | grep -E '\.(py|csv|json|md)$$' || true