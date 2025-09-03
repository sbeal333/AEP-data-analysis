#!/usr/bin/env python3
"""
Semantic transformation pipeline for AEP performance data.
Handles column renaming and business logic alignment for data integration.
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

class SemanticTransformer:
    """Transform cleaned data with semantic column names and business logic."""
    
    def __init__(self, input_path, output_path=None):
        """
        Initialize the semantic transformer.
        
        Args:
            input_path: Path to cleaned CSV file
            output_path: Path for semantically transformed data (optional)
        """
        self.input_path = Path(input_path)
        self.output_path = output_path
        self.df = None
        self.column_mapping = {}
        self.transformation_log = []
        
    def load_cleaned_data(self):
        """Load the cleaned CSV data."""
        logger.info(f"Loading cleaned data from {self.input_path}")
        self.df = pd.read_csv(self.input_path)
        logger.info(f"Loaded {len(self.df)} rows and {len(self.df.columns)} columns")
        return self
    
    def define_column_mapping(self):
        """
        Define the mapping from cleaned column names to semantic names.
        Edit this section to customize your column renaming.
        """
        logger.info("Defining column mapping for semantic transformation")
        
        # EDIT THIS SECTION: Add your desired column mappings
        self.column_mapping = {
            # Original cleaned name -> New semantic name
            
            # Identity/Hierarchy columns
            'manager_hierarchy_manager': 'manager_name',
            'manager_hierarchy_location': 'location',
            'manager_hierarchy_supervisor': 'supervisor_name', 
            'manager_hierarchy_name': 'agent_name',
            
            # Date columns
            'date_year': 'performance_year',
            'date_month': 'performance_month',
            'date_day': 'performance_day',
            'date': 'performance_date',
            'weekday': 'day_of_week',
            'week_number': 'week_of_year',
            'is_weekend': 'is_weekend_day',
            
            # Core performance metrics
            'talk': 'talk_time_seconds',
            'hold': 'hold_time_seconds', 
            'acw': 'after_call_work_seconds',
            'aht': 'average_handle_time_seconds',
            'interaction_count': 'total_interactions',
            
            # Quality metrics
            'osat_with_agent': 'customer_satisfaction_score',
            'resolution_rate': 'first_call_resolution_rate',
            'conformance': 'schedule_adherence_rate',
            
            # Availability metrics
            'talk_available_%': 'talk_time_availability_pct',
            'off_phone_%': 'off_phone_time_pct',
            
            # Sales/Transfer metrics
            'paperless_conversion': 'paperless_conversion_rate',
            'homeserve_transfers': 'homeserve_transfer_count',
            'allconnect_xfer/match_combo': 'allconnect_transfer_count',
            
            # Calculated metrics
            'performance_score': 'overall_performance_score',
            'calls_per_hour': 'hourly_interaction_rate',
        }
        
        # Log the mapping for review
        logger.info(f"Defined {len(self.column_mapping)} column mappings")
        self.transformation_log.append(f"Column mappings: {len(self.column_mapping)} defined")
        
        return self
    
    def apply_column_renaming(self):
        """Apply the column renaming based on the mapping."""
        logger.info("Applying semantic column renaming")
        
        # Check which columns exist in the data
        existing_mappings = {k: v for k, v in self.column_mapping.items() 
                           if k in self.df.columns}
        missing_columns = [k for k in self.column_mapping.keys() 
                          if k not in self.df.columns]
        
        # Log missing columns (not necessarily an error)
        if missing_columns:
            logger.warning(f"Columns not found in data: {missing_columns}")
            self.transformation_log.append(f"Missing columns: {missing_columns}")
        
        # Apply renaming
        self.df = self.df.rename(columns=existing_mappings)
        logger.info(f"Renamed {len(existing_mappings)} columns")
        self.transformation_log.append(f"Columns renamed: {len(existing_mappings)}")
        
        return self
    
    def add_business_logic_columns(self):
        """
        Add calculated columns with business logic.
        Edit this section to add custom business calculations.
        """
        logger.info("Adding business logic columns")
        
        # EDIT THIS SECTION: Add your business logic calculations
        
        # Example: Performance tier based on overall score
        if 'overall_performance_score' in self.df.columns:
            self.df['performance_tier'] = pd.cut(
                self.df['overall_performance_score'],
                bins=[0, 60, 75, 90, 100],
                labels=['Needs_Improvement', 'Meets_Expectations', 'Exceeds_Expectations', 'Outstanding'],
                include_lowest=True
            )
        
        # Example: High interaction day flag
        if 'total_interactions' in self.df.columns:
            median_interactions = self.df['total_interactions'].median()
            self.df['high_volume_day'] = self.df['total_interactions'] > median_interactions
        
        # Example: Efficiency category
        if 'hourly_interaction_rate' in self.df.columns:
            self.df['efficiency_category'] = pd.cut(
                self.df['hourly_interaction_rate'],
                bins=[0, 5, 10, 15, float('inf')],
                labels=['Low', 'Medium', 'High', 'Very_High'],
                include_lowest=True
            )
        
        # Add processing timestamp
        self.df['processed_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info("Business logic columns added")
        self.transformation_log.append("Business logic columns added")
        
        return self
    
    def standardize_data_types(self):
        """Ensure consistent data types for database compatibility."""
        logger.info("Standardizing data types for database compatibility")
        
        # EDIT THIS SECTION: Adjust data types as needed
        
        # Ensure percentage columns are proper decimals (0-1 range instead of 0-100)
        percentage_columns = [
            'talk_time_availability_pct', 'off_phone_time_pct', 
            'paperless_conversion_rate', 'first_call_resolution_rate',
            'schedule_adherence_rate', 'customer_satisfaction_score'
        ]
        
        for col in percentage_columns:
            if col in self.df.columns:
                # Convert from percentage (0-100) to decimal (0-1) if values > 1
                if self.df[col].max() > 1:
                    self.df[col] = self.df[col] / 100
        
        # Ensure integer columns are proper integers where appropriate
        integer_columns = [
            'performance_year', 'performance_day', 'week_of_year',
            'total_interactions', 'homeserve_transfer_count', 'allconnect_transfer_count'
        ]
        
        for col in integer_columns:
            if col in self.df.columns:
                # Replace infinite values with NaN and round to nearest integer
                self.df[col] = self.df[col].replace([np.inf, -np.inf], np.nan)
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')  # Ensure numeric
                self.df[col] = self.df[col].round().astype('Int64')  # Round then convert to nullable integer
        
        logger.info("Data types standardized")
        self.transformation_log.append("Data types standardized")
        
        return self
    
    def validate_transformation(self):
        """Validate the transformation results."""
        logger.info("Validating semantic transformation")
        
        # Basic validation checks
        validation_results = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'date_format_sample': self.df['performance_date'].dropna().head(3).tolist(),
            'column_names': self.df.columns.tolist(),
            'missing_critical_columns': []
        }
        
        # Check for critical columns
        critical_columns = ['agent_name', 'performance_date', 'overall_performance_score']
        for col in critical_columns:
            if col not in self.df.columns:
                validation_results['missing_critical_columns'].append(col)
        
        if validation_results['missing_critical_columns']:
            logger.warning(f"Missing critical columns: {validation_results['missing_critical_columns']}")
        else:
            logger.info("All critical columns present")
        
        self.validation_results = validation_results
        return self
    
    def save_transformed_data(self):
        """Save the semantically transformed data."""
        if self.output_path:
            output_file = Path(self.output_path)
        else:
            output_file = Path('data/processed') / f"aep_semantic_{datetime.now().strftime('%Y%m%d')}.csv"
        
        logger.info(f"Saving transformed data to {output_file}")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(output_file, index=False)
        
        # Save transformation log
        log_file = output_file.parent / f"semantic_transformation_log_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(log_file, 'w') as f:
            f.write("Semantic Transformation Log\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Input file: {self.input_path}\n")
            f.write(f"Output file: {output_file}\n")
            f.write(f"Transformation date: {datetime.now()}\n\n")
            
            f.write("Column Mapping Applied:\n")
            for old, new in self.column_mapping.items():
                if old in pd.read_csv(self.input_path, nrows=0).columns:
                    f.write(f"  {old} -> {new}\n")
            f.write("\n")
            
            f.write("Transformation Steps:\n")
            for step in self.transformation_log:
                f.write(f"  - {step}\n")
            f.write("\n")
            
            f.write("Validation Results:\n")
            for key, value in self.validation_results.items():
                f.write(f"  {key}: {value}\n")
        
        logger.info(f"Transformation log saved to {log_file}")
        return self
    
    def run_transformation(self):
        """Run the complete semantic transformation pipeline."""
        logger.info("Starting semantic transformation pipeline")
        
        (self
         .load_cleaned_data()
         .define_column_mapping()
         .apply_column_renaming()
         .add_business_logic_columns()
         .standardize_data_types()
         .validate_transformation()
         .save_transformed_data())
        
        logger.info("Semantic transformation pipeline complete")
        return self.df


if __name__ == "__main__":
    # Run the semantic transformation pipeline
    # Edit the input path to match your cleaned data file
    transformer = SemanticTransformer('data/processed/aep_cleaned_20250903.csv')
    transformed_df = transformer.run_transformation()
    
    print(f"\nTransformation complete!")
    print(f"Shape: {transformed_df.shape}")
    print(f"\nNew column names:")
    for i, col in enumerate(transformed_df.columns):
        print(f"  {i+1:2d}. {col}")
    
    print(f"\nSample of transformed data:")
    print(transformed_df[['agent_name', 'performance_date', 'overall_performance_score', 'performance_tier']].head(3))