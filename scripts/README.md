# AEP Data Analysis Scripts

This directory contains Python scripts for analyzing AEP performance data and candidate profiles.

## Scripts Overview

### `aep_candidate_analysis.py`
**Purpose**: Analyzes AEP performance data against portal applicants to identify successful candidate characteristics.

**What it does**:
1. ✅ Identifies all AEP clients in the portal system (8 different AEP divisions)
2. 🔍 Matches AEP performance data names to portal applicants who applied to AEP requisitions
3. 📊 Correlates resume scores and AI assessments with actual performance outcomes
4. 📈 Generates insights for candidate selection and AI model training

**Usage**:
```bash
cd scripts
source ../venv/bin/activate
python aep_candidate_analysis.py
```

**Output**:
- CSV file: `../data/processed/aep_candidate_analysis_YYYYMMDD_HHMMSS.csv`
- Console summary with key insights
- Analysis includes resume characteristics, AI predictions, and performance correlations

**Key Features**:
- **AEP-Focused**: Only analyzes candidates who applied to AEP requisitions
- **Smart Matching**: Uses name matching with date validation (application < performance date)
- **Rich Analysis**: Combines performance scores, resume analysis, and AI assessments
- **InnoSource Ready**: Generates data suitable for AI model training

### Other Scripts

**`data_cleaning.py`** - Cleans and processes raw AEP performance data
**`semantic_transformation.py`** - Transforms data for semantic analysis
**`top_performer_analysis.py`** - Identifies top performers from AEP data

## Data Flow

```
Raw AEP Data → data_cleaning.py → semantic_transformation.py → top_performer_analysis.py
                                                                          ↓
Portal Applicants ←→ aep_candidate_analysis.py ←→ Resume Scores + AI Assessments
                                                                          ↓
                                            Final Analysis CSV for InnoSource
```

## AEP Client Coverage

The analysis covers 8 AEP client divisions:
- AEP (ID: 53)
- AEP Energy (ID: 625)
- AEP Fort Wayne (ID: 623)
- AEP Gahanna (ID: 586)
- AEP Hurricane (ID: 587)
- AEP OSO (ID: 620)
- AEP OSO 626 (ID: 624)
- AEP Shreveport LA (ID: 628)

## Output Analysis

The generated CSV contains:
- **Candidate Info**: Names, application dates, contact info
- **Performance Data**: Actual performance scores and metrics
- **Resume Analysis**: AI-generated resume scores and characteristics
- **AI Predictions**: Jakib assessment scores and hiring recommendations
- **Success Validation**: How well AI predictions matched actual performance

## Integration Notes

**Database Queries**: The script is designed to work with the MCP (Model Context Protocol) connection to the data warehouse. SQL queries are embedded but executed via the MCP interface.

**Date Validation**: Ensures applicants applied BEFORE their performance data period to maintain data integrity.

**Scalability**: Script processes all 1,001 AEP performers but only matches against AEP-specific applicants for efficiency.