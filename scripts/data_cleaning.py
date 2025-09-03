#!/usr/bin/env python3
"""
Data cleaning pipeline for AEP performance data.
Handles data loading, validation, cleaning, and enrichment.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AEPDataCleaner:
    """Clean and process AEP performance data."""
    
    def __init__(self, input_path, output_path=None):
        """
        Initialize the data cleaner.
        
        Args:
            input_path: Path to raw CSV file
            output_path: Path for cleaned data (optional)
        """
        self.input_path = Path(input_path)
        self.output_path = output_path
        self.df = None
        self.data_quality_report = {}
        
    def load_data(self):
        """Load the raw CSV data."""
        logger.info(f"Loading data from {self.input_path}")
        self.df = pd.read_csv(self.input_path, encoding='utf-8-sig')
        logger.info(f"Loaded {len(self.df)} rows and {len(self.df.columns)} columns")
        return self
    
    def clean_column_names(self):
        """Standardize column names."""
        logger.info("Cleaning column names")
        self.df.columns = [col.strip().replace(' - ', '_').replace(' ', '_').lower() 
                          for col in self.df.columns]
        return self
    
    def parse_dates(self):
        """Create proper date column from year, month, day."""
        logger.info("Parsing date columns")
        
        # Create date column from components
        self.df['date'] = pd.to_datetime(
            self.df[['date_year', 'date_month', 'date_day']].rename(columns={
                'date_year': 'year',
                'date_month': 'month', 
                'date_day': 'day'
            }),
            errors='coerce'
        )
        
        # Add derived date columns
        self.df['weekday'] = self.df['date'].dt.day_name()
        self.df['week_number'] = self.df['date'].dt.isocalendar().week
        self.df['is_weekend'] = self.df['date'].dt.dayofweek.isin([5, 6])
        
        return self
    
    def clean_percentages(self):
        """Convert percentage strings to floats."""
        logger.info("Cleaning percentage columns")
        
        percentage_cols = [col for col in self.df.columns if '%' in self.df[col].astype(str).str.cat()]
        
        for col in percentage_cols:
            if col in self.df.columns:
                self.df[col] = (self.df[col]
                              .astype(str)
                              .str.rstrip('%')
                              .replace('', np.nan)
                              .astype(float))
        
        return self
    
    def handle_missing_values(self):
        """Handle missing values appropriately."""
        logger.info("Handling missing values")
        
        # Track missing values before handling
        missing_before = self.df.isnull().sum()
        self.data_quality_report['missing_values_before'] = missing_before[missing_before > 0].to_dict()
        
        # For time metrics, missing likely means no calls that day
        time_metrics = ['talk', 'hold', 'acw', 'aht']
        for col in time_metrics:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(0)
        
        # For percentages, keep as NaN for now
        # They'll be handled in calculations
        
        missing_after = self.df.isnull().sum()
        self.data_quality_report['missing_values_after'] = missing_after[missing_after > 0].to_dict()
        
        return self
    
    def add_calculated_metrics(self):
        """Add calculated fields and metrics."""
        logger.info("Adding calculated metrics")
        
        # Performance score (simple weighted average)
        if all(col in self.df.columns for col in ['talk_available_%', 'resolution_rate', 'conformance']):
            self.df['performance_score'] = (
                self.df['talk_available_%'] * 0.3 +
                self.df['resolution_rate'] * 0.4 +
                self.df['conformance'] * 0.3
            )
        
        # Efficiency ratio
        if 'interaction_count' in self.df.columns and 'aht' in self.df.columns:
            self.df['calls_per_hour'] = np.where(
                self.df['aht'] > 0,
                3600 / self.df['aht'],
                0
            )
        
        return self
    
    def validate_data(self):
        """Validate data quality and log issues."""
        logger.info("Validating data quality")
        
        # Check for duplicates
        duplicates = self.df.duplicated(subset=['manager_hierarchy_name', 'date']).sum()
        self.data_quality_report['duplicate_rows'] = duplicates
        
        # Check data types
        self.data_quality_report['column_types'] = self.df.dtypes.astype(str).to_dict()
        
        # Check value ranges
        if 'aht' in self.df.columns:
            self.data_quality_report['aht_range'] = {
                'min': self.df['aht'].min(),
                'max': self.df['aht'].max(),
                'mean': self.df['aht'].mean()
            }
        
        logger.info(f"Data validation complete. Found {duplicates} duplicate rows.")
        
        return self
    
    def save_cleaned_data(self):
        """Save the cleaned data to CSV."""
        if self.output_path:
            output_file = Path(self.output_path)
        else:
            output_file = Path('data/processed') / f"aep_cleaned_{datetime.now().strftime('%Y%m%d')}.csv"
        
        logger.info(f"Saving cleaned data to {output_file}")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(output_file, index=False)
        
        # Save data quality report
        report_file = output_file.parent / f"data_quality_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w') as f:
            f.write("Data Quality Report\n")
            f.write("=" * 50 + "\n\n")
            for key, value in self.data_quality_report.items():
                f.write(f"{key}:\n{value}\n\n")
        
        logger.info(f"Data quality report saved to {report_file}")
        
        return self
    
    def run_pipeline(self):
        """Run the complete cleaning pipeline."""
        logger.info("Starting data cleaning pipeline")
        
        (self
         .load_data()
         .clean_column_names()
         .parse_dates()
         .clean_percentages()
         .handle_missing_values()
         .add_calculated_metrics()
         .validate_data()
         .save_cleaned_data())
        
        logger.info("Data cleaning pipeline complete")
        return self.df


if __name__ == "__main__":
    # Run the cleaning pipeline
    cleaner = AEPDataCleaner('data/raw/aep-performance-data.csv')
    cleaned_df = cleaner.run_pipeline()
    
    print(f"\nCleaning complete!")
    print(f"Original shape: {len(cleaned_df)} rows x {len(cleaned_df.columns)} columns")
    print(f"\nColumns in cleaned dataset:")
    print(cleaned_df.columns.tolist())