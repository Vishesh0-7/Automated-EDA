"""
Comprehensive Automated EDA (Exploratory Data Analysis) Tool
Performs complete data analysis including statistics, visualizations, and reporting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import logging
from datetime import datetime
import warnings
from scipy import stats
import json

# Import visualization module
from .visualizations import EDAVisualizer

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AutomatedEDA:
    """
    Comprehensive Automated Exploratory Data Analysis class
    
    This class performs complete EDA including:
    - Data loading and basic information
    - Descriptive statistics
    - Missing data analysis
    - Outlier detection
    - Comprehensive visualizations
    - Automated reporting
    """
    
    def __init__(self, csv_path, output_dir="eda_output", enable_profiling=True):
        """
        Initialize the AutomatedEDA class
        
        Args:
            csv_path (str): Path to the CSV file
            output_dir (str): Directory to save output files
            enable_profiling (bool): Whether to generate profiling reports
        """
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.enable_profiling = enable_profiling
        self.data = None
        self.analysis_results = {}
        self.visualizer = None
        
        # Create output directories
        self._setup_output_directory()
        
        # Initialize visualizer
        self.visualizer = EDAVisualizer(self.output_dir)
        
        logger.info(f"AutomatedEDA initialized for file: {csv_path}")
    
    def _setup_output_directory(self):
        """Create output directory structure"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/plots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/reports", exist_ok=True)
        logger.info(f"Output directory structure created: {self.output_dir}")
    
    def load_data(self):
        """Load and validate the CSV data"""
        try:
            logger.info("📊 Loading data...")
            self.data = pd.read_csv(self.csv_path)
            
            logger.info(f"✅ Data loaded successfully!")
            logger.info(f"   - Shape: {self.data.shape}")
            logger.info(f"   - Columns: {list(self.data.columns)}")
            
            # Store basic info
            self.analysis_results['basic_info'] = {
                'file_path': self.csv_path,
                'shape': self.data.shape,
                'columns': list(self.data.columns),
                'data_types': self.data.dtypes.to_dict(),
                'memory_usage': self.data.memory_usage(deep=True).sum(),
                'load_timestamp': datetime.now().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            return False
    
    def analyze_basic_info(self):
        """Analyze basic dataset information"""
        logger.info("🔍 Analyzing basic dataset information...")
        
        if self.data is None:
            logger.error("No data loaded!")
            return
        
        # Basic statistics
        basic_stats = {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'numeric_columns': len(self.data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(self.data.select_dtypes(include=['object']).columns),
            'datetime_columns': len(self.data.select_dtypes(include=['datetime']).columns),
            'total_missing_values': self.data.isnull().sum().sum(),
            'missing_percentage': (self.data.isnull().sum().sum() / (len(self.data) * len(self.data.columns))) * 100,
            'duplicate_rows': self.data.duplicated().sum()
        }
        
        # Column-wise missing data
        missing_data = {
            'by_column': self.data.isnull().sum().to_dict(),
            'by_percentage': (self.data.isnull().sum() / len(self.data) * 100).to_dict()
        }
        
        # Unique values per column
        unique_values = {}
        for col in self.data.columns:
            unique_values[col] = {
                'count': self.data[col].nunique(),
                'percentage': (self.data[col].nunique() / len(self.data)) * 100
            }
        
        self.analysis_results['basic_stats'] = basic_stats
        self.analysis_results['missing_data'] = missing_data
        self.analysis_results['unique_values'] = unique_values
        
        logger.info(f"   - Total rows: {basic_stats['total_rows']:,}")
        logger.info(f"   - Total columns: {basic_stats['total_columns']}")
        logger.info(f"   - Missing values: {basic_stats['total_missing_values']:,} ({basic_stats['missing_percentage']:.2f}%)")
        logger.info(f"   - Duplicate rows: {basic_stats['duplicate_rows']:,}")
    
    def analyze_descriptive_statistics(self):
        """Generate comprehensive descriptive statistics"""
        logger.info("📈 Computing descriptive statistics...")
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        categorical_cols = self.data.select_dtypes(include=['object']).columns
        
        # Numeric statistics
        numeric_stats = {}
        if len(numeric_cols) > 0:
            desc_stats = self.data[numeric_cols].describe()
            
            for col in numeric_cols:
                numeric_stats[col] = {
                    'count': int(desc_stats.loc['count', col]),
                    'mean': desc_stats.loc['mean', col],
                    'median': self.data[col].median(),
                    'mode': self.data[col].mode().iloc[0] if len(self.data[col].mode()) > 0 else np.nan,
                    'std': desc_stats.loc['std', col],
                    'min': desc_stats.loc['min', col],
                    'max': desc_stats.loc['max', col],
                    'q25': desc_stats.loc['25%', col],
                    'q75': desc_stats.loc['75%', col],
                    'skewness': self.data[col].skew(),
                    'kurtosis': self.data[col].kurtosis(),
                    'variance': self.data[col].var()
                }
        
        # Categorical statistics
        categorical_stats = {}
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                value_counts = self.data[col].value_counts()
                categorical_stats[col] = {
                    'unique_count': self.data[col].nunique(),
                    'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'least_frequent': value_counts.index[-1] if len(value_counts) > 0 else None,
                    'least_frequent_count': int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
                    'top_5_values': value_counts.head().to_dict()
                }
        
        self.analysis_results['numeric_statistics'] = numeric_stats
        self.analysis_results['categorical_statistics'] = categorical_stats
        
        logger.info(f"   - Analyzed {len(numeric_cols)} numeric columns")
        logger.info(f"   - Analyzed {len(categorical_cols)} categorical columns")
    
    def detect_outliers(self, methods=['iqr', 'zscore']):
        """Detect outliers using multiple methods"""
        logger.info("🎯 Detecting outliers...")
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        outlier_results = {}
        
        for method in methods:
            outlier_results[method] = {}
            
            for col in numeric_cols:
                if method == 'iqr':
                    Q1 = self.data[col].quantile(0.25)
                    Q3 = self.data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = self.data[(self.data[col] < lower_bound) | (self.data[col] > upper_bound)]
                
                elif method == 'zscore':
                    z_scores = np.abs(stats.zscore(self.data[col].dropna()))
                    outlier_indices = np.where(z_scores > 3)[0]
                    outliers = self.data.iloc[outlier_indices]
                
                outlier_results[method][col] = {
                    'count': len(outliers),
                    'percentage': (len(outliers) / len(self.data)) * 100,
                    'indices': outliers.index.tolist()
                }
        
        self.analysis_results['outliers'] = outlier_results
        
        # Log summary
        total_outliers_iqr = sum([outlier_results['iqr'][col]['count'] for col in numeric_cols])
        logger.info(f"   - IQR method detected {total_outliers_iqr} outliers across all numeric columns")
        
        if 'zscore' in outlier_results:
            total_outliers_zscore = sum([outlier_results['zscore'][col]['count'] for col in numeric_cols])
            logger.info(f"   - Z-score method detected {total_outliers_zscore} outliers across all numeric columns")
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations"""
        logger.info("📊 Generating visualizations...")
        
        all_plots = []
        
        # Data overview plots
        logger.info("   - Creating data overview plots...")
        overview_plots = self.visualizer.create_summary_plots(self.data)
        all_plots.extend(overview_plots)
        
        # Missing data visualizations
        logger.info("   - Creating missing data visualizations...")
        missing_plots = self.visualizer.plot_missing_data(self.data)
        all_plots.extend(missing_plots)
        
        # Distribution plots
        logger.info("   - Creating distribution plots...")
        dist_plots = self.visualizer.plot_distributions(self.data)
        all_plots.extend(dist_plots)
        
        # Categorical plots
        logger.info("   - Creating categorical plots...")
        cat_plots = self.visualizer.plot_categorical(self.data)
        all_plots.extend(cat_plots)
        
        # Correlation heatmap
        logger.info("   - Creating correlation heatmap...")
        corr_plot = self.visualizer.plot_correlation_heatmap(self.data)
        if corr_plot:
            all_plots.append(corr_plot)
        
        # Pairplot
        logger.info("   - Creating pairplot...")
        pair_plot = self.visualizer.plot_pairplot(self.data)
        if pair_plot:
            all_plots.append(pair_plot)
        
        # Outlier plots
        logger.info("   - Creating outlier visualizations...")
        outlier_plots, outlier_info = self.visualizer.plot_outliers(self.data)
        all_plots.extend(outlier_plots)
        
        self.analysis_results['visualizations'] = {
            'plot_files': all_plots,
            'total_plots': len(all_plots)
        }
        
        logger.info(f"   ✅ Generated {len(all_plots)} visualization files")
    
    def generate_profiling_reports(self):
        """Generate automated profiling reports using ydata-profiling and sweetviz"""
        if not self.enable_profiling:
            logger.info("⏭️  Skipping profiling reports (disabled)")
            return
        
        logger.info("📋 Generating profiling reports...")
        
        try:
            # ydata-profiling report
            logger.info("   - Creating ydata-profiling report...")
            from ydata_profiling import ProfileReport
            
            profile = ProfileReport(
                self.data,
                title="Automated EDA Report",
                explorative=True,
                minimal=False
            )
            
            profile_path = f"{self.output_dir}/reports/ydata_profiling_report.html"
            profile.to_file(profile_path)
            logger.info(f"   ✅ ydata-profiling report saved: {profile_path}")
            
        except ImportError:
            logger.warning("   ⚠️  ydata-profiling not available, skipping...")
        except Exception as e:
            logger.error(f"   ❌ Error generating ydata-profiling report: {str(e)}")
        
        try:
            # Sweetviz report
            logger.info("   - Creating Sweetviz report...")
            import sweetviz as sv
            
            sweet_report = sv.analyze(self.data)
            sweet_path = f"{self.output_dir}/reports/sweetviz_report.html"
            sweet_report.show_html(sweet_path, open_browser=False)
            logger.info(f"   ✅ Sweetviz report saved: {sweet_path}")
            
        except ImportError:
            logger.warning("   ⚠️  Sweetviz not available, skipping...")
        except Exception as e:
            logger.error(f"   ❌ Error generating Sweetviz report: {str(e)}")
    
    def generate_summary_report(self):
        """Generate a comprehensive HTML summary report"""
        logger.info("📝 Generating summary report...")
        
        # Create HTML report
        html_content = self._create_html_report()
        
        # Save HTML report
        html_path = f"{self.output_dir}/eda_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save JSON summary
        json_path = f"{self.output_dir}/eda_summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            # Convert numpy types to native Python types for JSON serialization
            json_safe_results = self._convert_numpy_types(self.analysis_results)
            json.dump(json_safe_results, f, indent=2, default=str)
        
        logger.info(f"   ✅ HTML report saved: {html_path}")
        logger.info(f"   ✅ JSON summary saved: {json_path}")
        
        return html_path, json_path
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def _create_html_report(self):
        """Create comprehensive HTML report"""
        
        # Create a simple HTML report without complex CSS formatting
        basic_stats = self.analysis_results.get('basic_stats', {})
        
        # Generate content sections
        column_info_html = self._generate_column_info_html()
        numeric_stats_html = self._generate_numeric_stats_html()
        categorical_stats_html = self._generate_categorical_stats_html()
        key_findings_html = self._generate_key_findings_html()
        plot_images_html = self._generate_plot_images_html()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automated EDA Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-left: 4px solid #3498db; padding-left: 15px; }}
        .stat-grid {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; min-width: 150px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .stat-label {{ color: #7f8c8d; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .plot-grid {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
        .plot-container {{ text-align: center; max-width: 400px; }}
        .plot-container img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .key-findings {{ background: #667eea; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .findings-list {{ list-style: none; padding: 0; }}
        .findings-list li {{ margin: 10px 0; padding-left: 25px; }}
        .timestamp {{ text-align: center; color: #6c757d; font-style: italic; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Automated EDA Report</h1>
        <div class="timestamp">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        
        <div class="section">
            <h2>📊 Dataset Overview</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{basic_stats.get('total_rows', 0):,}</div>
                    <div class="stat-label">Total Rows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{basic_stats.get('total_columns', 0)}</div>
                    <div class="stat-label">Total Columns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{basic_stats.get('numeric_columns', 0)}</div>
                    <div class="stat-label">Numeric Columns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{basic_stats.get('categorical_columns', 0)}</div>
                    <div class="stat-label">Categorical Columns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{basic_stats.get('missing_percentage', 0):.1f}%</div>
                    <div class="stat-label">Missing Data</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{basic_stats.get('duplicate_rows', 0):,}</div>
                    <div class="stat-label">Duplicate Rows</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Key Findings</h2>
            <div class="key-findings">
                <h3 style="margin-top:0; color:white;">Summary of Important Insights</h3>
                {key_findings_html}
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Column Information</h2>
            {column_info_html}
        </div>
        
        {numeric_stats_html}
        
        {categorical_stats_html}
        
        <div class="section">
            <h2>📊 Visualizations</h2>
            <p>The following visualizations have been generated for your dataset:</p>
            {plot_images_html}
        </div>
        
        <div class="section">
            <h2>� Additional Resources</h2>
            <p><strong>Note:</strong> Additional detailed profiling reports may be available in the reports/ folder.</p>
        </div>
        
        <div class="timestamp">
            Report generated by Automated EDA Tool<br>
            File analyzed: {self.csv_path}
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def _generate_column_info_html(self):
        """Generate HTML for column information table"""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Column Name</th>
                    <th>Data Type</th>
                    <th>Non-Null Count</th>
                    <th>Missing %</th>
                    <th>Unique Values</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for col in self.data.columns:
            missing_pct = self.analysis_results['missing_data']['by_percentage'].get(col, 0)
            unique_count = self.analysis_results['unique_values'][col]['count']
            non_null_count = len(self.data) - self.analysis_results['missing_data']['by_column'].get(col, 0)
            
            html += f"""
                <tr>
                    <td><strong>{col}</strong></td>
                    <td>{str(self.data[col].dtype)}</td>
                    <td>{non_null_count:,}</td>
                    <td>{missing_pct:.1f}%</td>
                    <td>{unique_count:,}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        return html
    
    def _generate_numeric_stats_html(self):
        """Generate HTML for numeric statistics"""
        if 'numeric_statistics' not in self.analysis_results or not self.analysis_results['numeric_statistics']:
            return ""
        
        html = """
        <div class="section">
            <h2>📊 Numeric Statistics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Mean</th>
                        <th>Median</th>
                        <th>Std Dev</th>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Skewness</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for col, stats in self.analysis_results['numeric_statistics'].items():
            html += f"""
                <tr>
                    <td><strong>{col}</strong></td>
                    <td>{stats['mean']:.2f}</td>
                    <td>{stats['median']:.2f}</td>
                    <td>{stats['std']:.2f}</td>
                    <td>{stats['min']:.2f}</td>
                    <td>{stats['max']:.2f}</td>
                    <td>{stats['skewness']:.2f}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _generate_categorical_stats_html(self):
        """Generate HTML for categorical statistics"""
        if 'categorical_statistics' not in self.analysis_results or not self.analysis_results['categorical_statistics']:
            return ""
        
        html = """
        <div class="section">
            <h2>📝 Categorical Statistics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Unique Values</th>
                        <th>Most Frequent</th>
                        <th>Frequency</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for col, stats in self.analysis_results['categorical_statistics'].items():
            html += f"""
                <tr>
                    <td><strong>{col}</strong></td>
                    <td>{stats['unique_count']}</td>
                    <td>{stats['most_frequent']}</td>
                    <td>{stats['most_frequent_count']}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _generate_key_findings_html(self):
        """Generate HTML for key findings"""
        basic_stats = self.analysis_results.get('basic_stats', {})
        findings = []
        
        if basic_stats.get('missing_percentage', 0) > 10:
            findings.append(f"High missing data: {basic_stats['missing_percentage']:.1f}% of total values are missing")
        elif basic_stats.get('missing_percentage', 0) == 0:
            findings.append("No missing data found - dataset is complete")
        
        if basic_stats.get('duplicate_rows', 0) > 0:
            findings.append(f"Found {basic_stats['duplicate_rows']:,} duplicate rows")
        
        if 'numeric_statistics' in self.analysis_results:
            numeric_cols = list(self.analysis_results['numeric_statistics'].keys())
            if len(numeric_cols) > 1:
                findings.append(f"Dataset contains {len(numeric_cols)} numeric columns suitable for correlation analysis")
        
        if not findings:
            findings.append("Dataset appears to be well-structured with no major data quality issues")
        
        html = "<ul class='findings-list'>"
        for finding in findings:
            html += f"<li>{finding}</li>"
        html += "</ul>"
        
        return html
    
    def _generate_plot_images_html(self):
        """Generate HTML for plot images"""
        html = "<div class='plot-grid'>"
        
        if 'visualizations' in self.analysis_results:
            for plot_path in self.analysis_results['visualizations']['plot_files']:
                plot_name = os.path.basename(plot_path).replace('.png', '').replace('_', ' ').title()
                rel_plot_path = os.path.relpath(plot_path, self.output_dir)
                html += f"""
                    <div class="plot-container">
                        <h4>{plot_name}</h4>
                        <img src="{rel_plot_path}" alt="{plot_name}">
                    </div>
                """
        
        html += "</div>"
        return html
        
        # This method now uses the helper methods defined above
        
        return html_content
    
    def run_full_analysis(self):
        """Run the complete EDA pipeline"""
        logger.info("🚀 Starting comprehensive EDA analysis...")
        
        # Load data
        if not self.load_data():
            logger.error("❌ Failed to load data. Exiting.")
            return False
        
        # Run analysis steps
        try:
            self.analyze_basic_info()
            self.analyze_descriptive_statistics()
            self.detect_outliers()
            self.generate_visualizations()
            self.generate_profiling_reports()
            
            # Generate final report
            html_path, json_path = self.generate_summary_report()
            
            logger.info("🎉 EDA Analysis completed successfully!")
            logger.info(f"📄 Main report: {html_path}")
            logger.info(f"📊 Plots directory: {self.output_dir}/plots/")
            logger.info(f"📋 Additional reports: {self.output_dir}/reports/")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during analysis: {str(e)}")
            return False
