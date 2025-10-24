"""
Visualization utilities for Automated EDA
Contains functions for creating various plots and charts for data analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import missingno as msno
from scipy import stats
import warnings
import base64
from io import BytesIO

warnings.filterwarnings('ignore')

# Set style for matplotlib/seaborn
plt.style.use('default')
sns.set_palette("husl")


class EDAVisualizer:
    """Class containing all visualization methods for EDA"""
    
    def __init__(self, output_dir="eda_output"):
        self.output_dir = output_dir
        self.plot_paths = {}
        
    def save_plot(self, fig, filename, plot_type="matplotlib"):
        """Save plot to file and return path"""
        filepath = f"{self.output_dir}/plots/{filename}"
        
        if plot_type == "matplotlib":
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close(fig)
        elif plot_type == "plotly":
            fig.write_html(filepath.replace('.png', '.html'))
            fig.write_image(filepath)
        
        self.plot_paths[filename] = filepath
        return filepath
    
    def plot_missing_data(self, df):
        """Create comprehensive missing data visualizations"""
        plots_created = []
        
        # Missing data matrix
        fig, ax = plt.subplots(figsize=(12, 6))
        msno.matrix(df, ax=ax)
        plt.title('Missing Data Matrix', fontsize=16, fontweight='bold')
        path = self.save_plot(fig, 'missing_data_matrix.png')
        plots_created.append(path)
        
        # Missing data bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        msno.bar(df, ax=ax)
        plt.title('Missing Data Count by Column', fontsize=16, fontweight='bold')
        path = self.save_plot(fig, 'missing_data_bar.png')
        plots_created.append(path)
        
        # Missing data heatmap (correlation of missingness)
        if df.isnull().sum().sum() > 0:  # Only if there's missing data
            fig, ax = plt.subplots(figsize=(10, 8))
            msno.heatmap(df, ax=ax)
            plt.title('Missing Data Correlation Heatmap', fontsize=16, fontweight='bold')
            path = self.save_plot(fig, 'missing_data_heatmap.png')
            plots_created.append(path)
        
        return plots_created
    
    def plot_distributions(self, df):
        """Create distribution plots for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        plots_created = []
        
        if len(numeric_cols) == 0:
            return plots_created
        
        # Individual histograms with KDE
        for col in numeric_cols:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # Histogram with KDE
            sns.histplot(data=df, x=col, kde=True, ax=ax1)
            ax1.set_title(f'Distribution of {col}', fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # Box plot
            sns.boxplot(data=df, y=col, ax=ax2)
            ax2.set_title(f'Box Plot of {col}', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            path = self.save_plot(fig, f'distribution_{col.replace(" ", "_")}.png')
            plots_created.append(path)
        
        # Combined distributions
        if len(numeric_cols) > 1:
            n_cols = min(3, len(numeric_cols))
            n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
            if n_rows == 1:
                axes = [axes] if n_cols == 1 else axes
            elif n_cols == 1:
                axes = [[ax] for ax in axes]
            
            for i, col in enumerate(numeric_cols):
                row = i // n_cols
                col_idx = i % n_cols
                ax = axes[row][col_idx] if n_rows > 1 else axes[col_idx]
                
                sns.histplot(data=df, x=col, kde=True, ax=ax)
                ax.set_title(f'{col}', fontweight='bold')
                ax.grid(True, alpha=0.3)
            
            # Hide empty subplots
            for i in range(len(numeric_cols), n_rows * n_cols):
                row = i // n_cols
                col_idx = i % n_cols
                ax = axes[row][col_idx] if n_rows > 1 else axes[col_idx]
                ax.set_visible(False)
            
            plt.tight_layout()
            path = self.save_plot(fig, 'all_distributions.png')
            plots_created.append(path)
        
        return plots_created
    
    def plot_categorical(self, df):
        """Create count plots for categorical columns"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        plots_created = []
        
        if len(categorical_cols) == 0:
            return plots_created
        
        for col in categorical_cols:
            # Skip columns with too many unique values
            if df[col].nunique() > 20:
                continue
                
            fig, ax = plt.subplots(figsize=(12, 6))
            
            value_counts = df[col].value_counts().head(10)  # Top 10 categories
            
            sns.countplot(data=df[df[col].isin(value_counts.index)], x=col, ax=ax)
            ax.set_title(f'Count Plot: {col}', fontsize=16, fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, v in enumerate(value_counts.values):
                ax.text(i, v + max(value_counts) * 0.01, str(v), 
                       ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            path = self.save_plot(fig, f'countplot_{col.replace(" ", "_")}.png')
            plots_created.append(path)
        
        return plots_created
    
    def plot_correlation_heatmap(self, df):
        """Create correlation heatmap for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return None
        
        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create mask for upper triangle (optional)
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(corr_matrix, 
                   mask=mask,
                   annot=True, 
                   fmt='.2f', 
                   cmap='RdBu_r',
                   center=0,
                   square=True,
                   ax=ax)
        
        ax.set_title('Correlation Heatmap', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return self.save_plot(fig, 'correlation_heatmap.png')
    
    def plot_pairplot(self, df, sample_size=1000):
        """Create pairplot for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return None
        
        # Sample data if too large
        plot_df = df if len(df) <= sample_size else df.sample(sample_size)
        
        # Limit to first 5 numeric columns to avoid overcrowding
        cols_to_plot = numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols
        
        fig = sns.pairplot(plot_df[cols_to_plot], 
                          diag_kind='hist',
                          plot_kws={'alpha': 0.6})
        
        fig.fig.suptitle('Pairplot of Numeric Features', y=1.02, fontsize=16, fontweight='bold')
        
        return self.save_plot(fig.fig, 'pairplot.png')
    
    def plot_outliers(self, df, method='iqr'):
        """Detect and visualize outliers"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        plots_created = []
        
        if len(numeric_cols) == 0:
            return plots_created, {}
        
        outlier_info = {}
        
        for col in numeric_cols:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # Box plot
            sns.boxplot(data=df, y=col, ax=ax1)
            ax1.set_title(f'Box Plot: {col}', fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # Scatter plot with outliers highlighted
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            else:  # z-score method
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                outliers = df[z_scores > 3]
            
            # Scatter plot
            ax2.scatter(range(len(df)), df[col], alpha=0.6, c='blue', label='Normal')
            if len(outliers) > 0:
                outlier_indices = outliers.index
                ax2.scatter(outlier_indices, df.loc[outlier_indices, col], 
                           c='red', s=50, label='Outliers', alpha=0.8)
            
            ax2.set_title(f'Outliers in {col} ({method.upper()} method)', fontweight='bold')
            ax2.set_xlabel('Index')
            ax2.set_ylabel(col)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            path = self.save_plot(fig, f'outliers_{col.replace(" ", "_")}.png')
            plots_created.append(path)
            
            # Store outlier information
            outlier_info[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(df)) * 100,
                'method': method
            }
        
        return plots_created, outlier_info
    
    def create_summary_plots(self, df):
        """Create summary overview plots"""
        plots_created = []
        
        # Data types distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Column types
        dtype_counts = df.dtypes.value_counts()
        dtype_counts.plot(kind='pie', ax=ax1, autopct='%1.1f%%')
        ax1.set_title('Distribution of Data Types', fontweight='bold')
        ax1.set_ylabel('')
        
        # Missing data percentage
        missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
        missing_pct = missing_pct[missing_pct > 0]  # Only show columns with missing data
        
        if len(missing_pct) > 0:
            missing_pct.plot(kind='bar', ax=ax2, color='red', alpha=0.7)
            ax2.set_title('Missing Data Percentage by Column', fontweight='bold')
            ax2.set_xlabel('Columns')
            ax2.set_ylabel('Missing %')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, 'No Missing Data Found!', 
                    ha='center', va='center', transform=ax2.transAxes,
                    fontsize=14, fontweight='bold')
            ax2.set_title('Missing Data Status', fontweight='bold')
        
        plt.tight_layout()
        path = self.save_plot(fig, 'data_overview.png')
        plots_created.append(path)
        
        return plots_created