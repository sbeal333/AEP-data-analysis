# Technical Stack

> Last Updated: 2025-01-03
> Version: 1.0.0

## Core Technologies

### Programming Language
- **Language:** Python
- **Version:** 3.11+

### Data Analysis Libraries
- **pandas:** 2.0+ - Data manipulation and analysis
- **numpy:** 1.24+ - Numerical computing
- **openpyxl:** 3.1+ - Excel file operations
- **python-dotenv:** 1.0+ - Environment variable management

### Data Integration & Export
- **requests:** 2.31+ - API integration for InnoSource data exchange
- **fuzzywuzzy:** 0.18+ - Fuzzy string matching for candidate linking
- **python-levenshtein:** 0.20+ - String distance calculations
- **jsonschema:** 4.17+ - JSON validation for export formats

### Visualization Libraries
- **matplotlib:** 3.7+ - Static plotting
- **plotly:** 5.0+ - Interactive visualizations
- **seaborn:** 0.12+ - Statistical data visualization

### Development Tools
- **VS Code:** Primary development environment
- **Python virtual environment:** Dependency isolation
- **Git:** Version control

## Project Structure

### Directory Organization
- **data/** - Raw and processed data files
- **scripts/** - Python analysis scripts
- **reports/** - Generated analysis reports
- **config/** - Configuration files

### File Formats
- **Input:** CSV, Excel, JSON (from InnoSource API)
- **Output:** CSV, JSON, HTML reports, AI training datasets
- **AI Export:** JSON with structured candidate/performance data
- **Documentation:** Markdown

## Infrastructure

### Local Development
- **Platform:** macOS/Linux/Windows
- **Python Environment:** venv or conda
- **Package Manager:** pip

### Data Storage
- **Local Files:** CSV and Excel files
- **Version Control:** Git for code and documentation
- **Data Backup:** Local backups of processed data

## Deployment

### Execution Environment
- **Type:** Local Python scripts
- **Scheduling:** Manual execution or cron jobs
- **Output:** File-based reports

### Code Repository
- **Platform:** GitHub/GitLab
- **Strategy:** Feature branches with main branch protection

## External Integrations

### InnoSource AI Partnership
- **Data Exchange:** JSON-based export format
- **Integration Method:** File-based export with API endpoints (future)
- **Authentication:** Secure data transfer protocols
- **Frequency:** Quarterly data exports or on-demand

### Data Sources Required
- **InnoSource:** AI rating data, candidate profiles, model metadata
- **AEP Systems:** Performance data, candidate ratings, resume data
- **Integration:** Candidate matching via fuzzy logic and unique identifiers