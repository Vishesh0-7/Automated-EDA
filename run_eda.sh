#!/bin/bash

# Automated EDA Tool - Quick Run Script
# This script provides easy access to the EDA tool with common options

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show usage
show_usage() {
    echo "🔍 Automated EDA Tool - Quick Run Script"
    echo "======================================"
    echo ""
    echo "Usage: $0 [OPTIONS] <csv-file>"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -o, --output-dir    Output directory (default: eda_output)"
    echo "  -n, --no-profiling  Skip profiling reports (faster execution)"
    echo "  -e, --example       Run with example data"
    echo ""
    echo "Examples:"
    echo "  $0 data/loan_approval.csv"
    echo "  $0 -o my_analysis data/dataset.csv"
    echo "  $0 --no-profiling data/large_dataset.csv"
    echo "  $0 --example"
    echo ""
}

# Default values
OUTPUT_DIR="eda_output"
NO_PROFILING=""
CSV_FILE=""
RUN_EXAMPLE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -n|--no-profiling)
            NO_PROFILING="--no-profiling"
            shift
            ;;
        -e|--example)
            RUN_EXAMPLE=true
            shift
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$CSV_FILE" ]; then
                CSV_FILE="$1"
            else
                print_error "Multiple CSV files specified. Please provide only one."
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    print_warning "Python virtual environment not found. Setting up..."
    python3 -m venv .venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating Python environment..."
source .venv/bin/activate

# Check if packages are installed
print_info "Checking dependencies..."
if ! python -c "import pandas, matplotlib, seaborn" 2>/dev/null; then
    print_warning "Installing required packages..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
fi

# Handle example run
if [ "$RUN_EXAMPLE" = true ]; then
    print_info "Running example analysis..."
    python example_usage.py
    exit 0
fi

# Validate CSV file
if [ -z "$CSV_FILE" ]; then
    print_error "No CSV file specified"
    show_usage
    exit 1
fi

if [ ! -f "$CSV_FILE" ]; then
    print_error "CSV file not found: $CSV_FILE"
    exit 1
fi

# Run EDA analysis
print_info "Starting Automated EDA analysis..."
print_info "File: $CSV_FILE"
print_info "Output: $OUTPUT_DIR"

# Build command
CMD="python automated_eda.py --file \"$CSV_FILE\" --output-dir \"$OUTPUT_DIR\" $NO_PROFILING"

# Execute command
eval $CMD

# Check if analysis was successful
if [ $? -eq 0 ]; then
    echo ""
    print_success "EDA Analysis completed successfully!"
    print_info "Results saved to: $OUTPUT_DIR/"
    print_info "Open $OUTPUT_DIR/eda_report.html to view the report"
    
    # Try to open the report in browser (Linux)
    if command -v xdg-open &> /dev/null; then
        print_info "Opening report in browser..."
        xdg-open "$OUTPUT_DIR/eda_report.html" &
    fi
else
    print_error "EDA Analysis failed"
    exit 1
fi