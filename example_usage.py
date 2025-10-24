#!/usr/bin/env python3
"""
Example usage script for the Automated EDA tool
This script demonstrates how to use the tool programmatically
"""

from src.main_eda import AutomatedEDA
import pandas as pd
import numpy as np

def create_sample_dataset():
    """Create a sample dataset for demonstration"""
    np.random.seed(42)
    
    # Generate sample data
    n_samples = 1000
    
    data = {
        'age': np.random.normal(35, 10, n_samples),
        'salary': np.random.exponential(50000, n_samples),
        'experience_years': np.random.poisson(5, n_samples),
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR'], n_samples),
        'education': np.random.choice(['Bachelor', 'Master', 'PhD', 'High School'], n_samples, p=[0.4, 0.3, 0.1, 0.2]),
        'performance_score': np.random.beta(2, 5, n_samples) * 100,
        'satisfaction': np.random.uniform(1, 10, n_samples)
    }
    
    # Introduce some missing values
    missing_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
    data['satisfaction'][missing_indices] = np.nan
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('data/sample_employee_data.csv', index=False)
    print("✅ Sample dataset created: data/sample_employee_data.csv")
    
    return 'data/sample_employee_data.csv'

def run_example_analysis():
    """Run example EDA analysis"""
    print("🚀 Running Automated EDA Example")
    print("="*50)
    
    # Create sample data
    sample_file = create_sample_dataset()
    
    # Initialize EDA tool
    eda = AutomatedEDA(
        csv_path=sample_file,
        output_dir="example_output",
        enable_profiling=False  # Skip profiling for faster execution
    )
    
    # Run analysis
    success = eda.run_full_analysis()
    
    if success:
        print("\n🎉 Example analysis completed successfully!")
        print("📄 Check 'example_output/eda_report.html' for results")
    else:
        print("\n❌ Example analysis failed")

def demonstrate_api_usage():
    """Demonstrate programmatic API usage"""
    print("\n🔧 API Usage Example")
    print("="*30)
    
    # Load the loan approval dataset
    eda = AutomatedEDA(
        csv_path='data/loan_approval.csv',
        output_dir="api_example_output",
        enable_profiling=False
    )
    
    # Load data
    if eda.load_data():
        print(f"📊 Dataset shape: {eda.data.shape}")
        
        # Run individual analysis steps
        eda.analyze_basic_info()
        print(f"📈 Basic stats computed")
        
        eda.analyze_descriptive_statistics()
        print(f"📊 Descriptive statistics computed")
        
        eda.detect_outliers()
        print(f"🎯 Outliers detected")
        
        # Access results programmatically
        basic_stats = eda.analysis_results.get('basic_stats', {})
        print(f"\n📋 Key Statistics:")
        print(f"   - Total rows: {basic_stats.get('total_rows', 0):,}")
        print(f"   - Missing data: {basic_stats.get('missing_percentage', 0):.2f}%")
        print(f"   - Numeric columns: {basic_stats.get('numeric_columns', 0)}")
        print(f"   - Categorical columns: {basic_stats.get('categorical_columns', 0)}")

if __name__ == "__main__":
    print("🔍 Automated EDA Tool - Example Usage")
    print("="*50)
    
    # Run complete example
    run_example_analysis()
    
    # Demonstrate API usage
    demonstrate_api_usage()
    
    print("\n✨ Examples completed!")
    print("💡 Try running: python automated_eda.py --file data/loan_approval.csv")