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
        
        # Create date column from components (month is text like "January")
        date_df = self.df[['date_year', 'date_month', 'date_day']].copy()
        date_df['date_combined'] = (
            date_df['date_year'].astype(str) + '-' + 
            date_df['date_month'].astype(str) + '-' + 
            date_df['date_day'].astype(str)
        )
        
        # Parse the combined date string
        parsed_dates = pd.to_datetime(date_df['date_combined'], errors='coerce')
        
        # Format date as YYYY-MM-DD string for PostgreSQL compatibility
        self.df['date'] = parsed_dates.dt.strftime('%Y-%m-%d')
        
        # Add derived date columns
        self.df['weekday'] = parsed_dates.dt.day_name()
        self.df['week_number'] = parsed_dates.dt.isocalendar().week.astype('Int64')
        self.df['is_weekend'] = parsed_dates.dt.dayofweek.isin([5, 6])
        
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
    
    def fix_data_types(self):
        """Fix data types for problematic columns."""
        logger.info("Fixing data types")
        
        # Fix interaction_count - convert to numeric, coercing errors to NaN
        if 'interaction_count' in self.df.columns:
            self.df['interaction_count'] = pd.to_numeric(
                self.df['interaction_count'], 
                errors='coerce'
            ).astype('Int64')  # Use nullable integer type
        
        # Ensure numeric columns are properly typed
        numeric_cols = [
            'talk', 'hold', 'acw', 'aht', 'paperless_conversion', 
            'homeserve_transfers', 'allconnect_xfer/match_combo',
            'osat_with_agent', 'resolution_rate', 'talk_available_%',
            'off_phone_%', 'conformance'
        ]
        
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Ensure date components are proper integers
        if 'date_year' in self.df.columns:
            self.df['date_year'] = self.df['date_year'].astype('Int64')
        if 'date_day' in self.df.columns:
            self.df['date_day'] = self.df['date_day'].astype('Int64')
            
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
                (self.df['aht'] > 0) & (self.df['aht'] < np.inf),
                3600 / self.df['aht'],
                0
            )
        
        return self
    
    def parse_agent_names(self):
        """Parse agent names into separate first, last, and middle initial fields."""
        logger.info("Parsing agent names into separate fields")
        
        if 'manager_hierarchy_name' not in self.df.columns:
            logger.warning("manager_hierarchy_name column not found, skipping name parsing")
            return self
        
        # Parse names in format "LASTNAME,FIRSTNAME MIDDLEINITIAL"
        def parse_name(name_str):
            if pd.isna(name_str) or not isinstance(name_str, str):
                return pd.Series([None, None, None])
            
            # Clean the name string
            name_str = str(name_str).strip()
            
            # Split on comma
            parts = name_str.split(',')
            if len(parts) != 2:
                # Handle edge cases where format doesn't match expected pattern
                return pd.Series([None, None, None])
            
            last_name = parts[0].strip()
            first_part = parts[1].strip()
            
            # Split first part on spaces to separate first name and middle initial
            name_parts = first_part.split()
            
            if len(name_parts) == 0:
                first_name = None
                middle_initial = None
            elif len(name_parts) == 1:
                first_name = name_parts[0]
                middle_initial = None
            else:
                first_name = name_parts[0]
                # Take the first character of the last part as middle initial
                middle_initial = name_parts[-1][0] if name_parts[-1] else None
            
            return pd.Series([last_name, first_name, middle_initial])
        
        # Apply the name parsing
        name_columns = self.df['manager_hierarchy_name'].apply(parse_name)
        name_columns.columns = ['agent_last_name', 'agent_first_name', 'agent_middle_initial']
        
        # Add the new columns to the dataframe
        self.df = pd.concat([self.df, name_columns], axis=1)
        
        logger.info("Agent name parsing complete")
        
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
         .fix_data_types()
         .handle_missing_values()
         .add_calculated_metrics()
         .parse_agent_names()
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