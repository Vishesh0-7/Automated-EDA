#!/usr/bin/env python3
"""
Automated EDA (Exploratory Data Analysis) Tool
Author: AI Assistant
Date: October 2025

This script performs comprehensive exploratory data analysis on CSV files.
Usage: python automated_eda.py --file path/to/your/data.csv
"""

import argparse
import os
import sys
from src.main_eda import AutomatedEDA


def main():
    """Main function to run the automated EDA process"""
    parser = argparse.ArgumentParser(
        description='Automated Exploratory Data Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python automated_eda.py --file data/loan_approval.csv
  python automated_eda.py --file /path/to/your/dataset.csv
        """
    )
    
    parser.add_argument(
        '--file', 
        type=str, 
        required=True,
        help='Path to the CSV file for analysis'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='eda_output',
        help='Directory to save EDA results (default: eda_output)'
    )
    
    parser.add_argument(
        '--no-profiling',
        action='store_true',
        help='Skip automated profiling reports (faster execution)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.file):
        print(f"❌ Error: File '{args.file}' not found!")
        sys.exit(1)
    
    if not args.file.lower().endswith('.csv'):
        print(f"❌ Error: File must be a CSV file. Got: {args.file}")
        sys.exit(1)
    
    try:
        # Initialize and run EDA
        print(f"🚀 Starting Automated EDA for: {args.file}")
        eda = AutomatedEDA(
            csv_path=args.file,
            output_dir=args.output_dir,
            enable_profiling=not args.no_profiling
        )
        
        # Run the complete EDA pipeline
        eda.run_full_analysis()
        
        print(f"\n✅ EDA Complete! Results saved to: {args.output_dir}/")
        print(f"📊 Open '{args.output_dir}/eda_report.html' to view the full report")
        
    except Exception as e:
        print(f"❌ Error during EDA: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()